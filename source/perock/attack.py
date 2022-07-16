'''
Communicates with target/system and also analyse responce on 
single attempt.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
import asyncio
import time 

from .attempt import Attempt
from .attempt import AttemptAsync

from .check import Check
from .check import CheckAsync

from .responce import BytesCompare


class Attack(Attempt, Check):
    '''Attempts to logs into system with data'''
    base_attempt_class = Attempt
    base_check_class = Check

    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data)
        # Multiple inheritance is causing problems
        # Hope __init__(self, self) wont cause problems
        # Note that Check class composites Attempt class
        # As 'self' is subclass(derived) of Attempt
        # It can be passed in place of Attempt object
        # I hope this does not add performance overhead(but it works)
        self.base_check_class.__init__(self, self)
        self._retries = retries
        self._retry_sleep_time = 0
        self._retries_started = False

        self._request_until = False

    def set_retries(self, retries):
        self._retries = retries

    def set_retries_sleep_time(self, seconds):
        self._retry_sleep_time = seconds

    def enable_request_until(self):
        # Enables requesting until target is reached
        self._request_until = True

    def disable_request_until(self):
        # Enables requesting until target is reached
        self._request_until = False

    def _validate_attack(self):
        target_reached = self.target_reached()
        request_failed = self.request_failed()
        request_started = self.request_started()

        target_errors = self.target_errors()
        client_errors = self.client_errors()
        errors = self.errors()

        failure = self.failure()
        success = self.success()

        main_results = [errors, success, failure]

        if not request_started:
            if target_reached:
                err_msg = "Target cant be reached while request was not started"
                raise Exception(err_msg)
            if request_failed:
                err_msg = "Request cant fail if request was not started"
                raise Exception(err_msg)
            if any(main_results):
                err_msg = "errors, success or failure not expected if "
                "request was not started"
                raise Exception(err_msg)

        if request_failed:
            if not isinstance(self.responce, Exception):
                err_msg = "Responce should be exception if request failed"
                raise Exception(err_msg, type(self.responce))
            if not client_errors:
                err_msg = "Client error expected if request failed"
                raise Exception(err_msg)
            if target_errors:
                err_msg = "Target error not allowed if request failed"
                raise Exception(err_msg)

        if target_reached:
            if request_failed:
                err_msg = "Request cant fail if target was reached"
                raise Exception(err_msg)
            if client_errors:
                err_msg = "Client error not expected if target was reached"
                raise Exception(err_msg)
            if len(list(filter(None, [main_results]))) != 1:
                err_msg = "Only one between success, failure and errors " +\
                f"expected, not {len(list(filter(None, [main_results])))}" +\
                "if target was reached"
                raise Exception(err_msg)

        if not target_reached:
            if target_errors:
                err_msg = "Target error not expected if target was not reached"
                raise Exception(err_msg)
            if success and failure:
                err_msg = "success or failure  not expected if target " +\
                "was not reached"
                raise Exception(err_msg)
                    

        if errors and not (client_errors or target_errors):
            err_msg = "Errors encounted but no client or target errors"
            raise Exception(err_msg)

        if success and failure:
            err_msg = "success and failure cant happen at the same time"
            raise Exception(err_msg)

        if errors and (success or failure):
            err_msg = "Error not expected if theres success or failure"
            raise Exception(err_msg)

    def _update_responce_message(self):        
        if self.target_reached():
            self.responce_msg = "Target was reached"
            if self.target_errors():
                self.responce_msg = "Target experienced errors"
            elif self.failure():
                self.responce_msg = "Failed to crack target(failure)"
            elif self.success():
                self.responce_msg = "Target was cracked(success)"
        else:
            self.responce_msg = "Target was not reached"
            if not self.request_started():
                self.responce_msg = "Request was not started"
            elif self.request_failed():
                # Request failed, responce should be exception.
                self.responce_msg = str(self.responce)
            elif self.client_errors():
                self.responce_msg = "Client experienced errors"
            else:
                err_msg = "Target not reached for unknown reasons"
                raise Exception(err_msg)

    def isconfused(self):
        # Returns True the object is aware of state of responce
        results = any([
            self.errors(),
            self.failure(),
            self.success()
        ])
        return not results

    def confused_action(self):
        # Method called if theres is confusion
        err_msg = f'''
        Not sure if attack failed or was success(confused)

        Record/Data: {self.data}
        Target Reached: {self.target_reached()}
        Errors: {self.errors()}
        Failed: {self.failure()}
        Success: {self.success()}
        '''
        raise Exception(err_msg)  

    def start_until_target_reached(self):
        # Starts requests for retries until target is reached
        # No need to retry if running until
        self._retries = 0
        while True:
            self.start()
            time.sleep(self._retry_sleep_time)
            if self.target_reached():
                break

    def target_not_reached_action(self):
        # Method called if target is not reached
        # self._retries_started prevents recursion
        if not self._retries_started:
            self._retries_started = True
            for _ in range(self._retries):
                self.start()
                time.sleep(self._retry_sleep_time)
                if self.target_reached():
                    break

    def after_request(self):
        # Called after start() completes
        super().after_request()
        self._validate_attack()
        self._update_responce_message()
        if self.isconfused():
            self.confused_action()
        if not self.target_reached():
            self.target_not_reached_action()

    def start(self):
        if self._request_until:
            self._request_until = False
            self.start_until_target_reached()
            self._request_until = True
        else:
            super().start()


class AttackText(Attack, BytesCompare):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        BytesCompare.__init__(self, b"")
        super().__init__(target, data, retries)

    def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    def success(self) -> bool:
        return BytesCompare.success(self)

    def failure(self) -> bool:
        return BytesCompare.failure(self)

    def target_errors(self) -> bool:
        return BytesCompare.target_error(self)

    def client_errors(self) -> bool:
        if super().client_errors():
            return True
        return BytesCompare.target_error(self)

    def errors(self) -> bool:
        if super().errors():
            return True
        return BytesCompare.error(self)       

    def after_request(self):
        # Careful of when to call super().after_request()
        responce_content = self.responce_content()
        responce_bytes = self._create_responce_bytes(responce_content)
        self._responce_bytes = responce_bytes
        super().after_request()



# -----------------------------------------------
# Classes from here are for attack async classes
# -----------------------------------------------



class AttackAsync(AttemptAsync, CheckAsync):
    '''Perform attack using request implemeted with asyncio'''
    base_attempt_class = AttemptAsync
    base_check_class = CheckAsync

    def __init__(self, target, data: dict, retries=1) -> None:
        self.base_attempt_class.__init__(self, target, data, retries)
        self.base_check_class.__init__(self, self)
        self._retries = 10
        self._retry_sleep_time = 0
        self._retries_started = False


        self._retries = retries
        self._retry_sleep_time = 0
        self._retries_started = False

        self._request_until = False

    def set_retries(self, retries):
        self._retries = retries

    def set_retries_sleep_time(self, seconds):
        self._retry_sleep_time = seconds

    def enable_request_until(self):
        # Enables requesting until target is reached
        self._request_until = True

    def disable_request_until(self):
        # Enables requesting until target is reached
        self._request_until = False


    async def _validate_attack(self):
        target_reached = await self.target_reached()
        request_failed = self.request_failed()
        request_started = self.request_started()

        target_errors = await self.target_errors()
        client_errors = await self.client_errors()
        errors = await self.errors()

        failure = await self.failure()
        success = await self.success()

        main_results = [errors, success, failure]

        if not request_started:
            if target_reached:
                err_msg = "Target cant be reached while request was not started"
                raise Exception(err_msg)
            if request_failed:
                err_msg = "Request cant fail if request was not started"
                raise Exception(err_msg)
            if any(main_results):
                err_msg = "errors, success or failure not expected if "
                "request was not started"
                raise Exception(err_msg)

        if request_failed:
            if not isinstance(self.responce, Exception):
                err_msg = "Responce should be exception if request failed"
                raise Exception(err_msg, type(self.responce))
            if not client_errors:
                err_msg = "Client error expected if request failed"
                raise Exception(err_msg)
            if target_errors:
                err_msg = "Target error not allowed if request failed"
                raise Exception(err_msg)

        if target_reached:
            if request_failed:
                err_msg = "Request cant fail if target was reached"
                raise Exception(err_msg)
            if client_errors:
                err_msg = "Client error not expected if target was reached"
                raise Exception(err_msg)
            if len(list(filter(None, [main_results]))) != 1:
                err_msg = "Only one between success, failure and errors " +\
                f"expected, not {len(list(filter(None, [main_results])))}" +\
                "if target was reached"
                raise Exception(err_msg)

        if not target_reached:
            if target_errors:
                err_msg = "Target error not expected if target was not reached"
                raise Exception(err_msg)
            if success and failure:
                err_msg = "success or failure  not expected if target " +\
                "was not reached"
                raise Exception(err_msg)
                    

        if errors and not (client_errors or target_errors):
            err_msg = "Errors encounted but no client or target errors"
            raise Exception(err_msg)

        if success and failure:
            err_msg = "success and failure cant happen at the same time"
            raise Exception(err_msg)

        if errors and (success or failure):
            err_msg = "Error not expected if theres success or failure"
            raise Exception(err_msg)

    async def _update_responce_message(self):     
        target_reached = await self.target_reached()
        request_failed = self.request_failed()
        request_started = self.request_started()

        target_errors = await self.target_errors()
        client_errors = await self.client_errors()

        failure = await self.failure()
        success = await self.success()
   
        if target_reached:
            self.responce_msg = "Target was reached"
            if target_errors:
                self.responce_msg = "Target experienced errors"
            elif failure:
                self.responce_msg = "Failed to crack target(failure)"
            elif success:
                self.responce_msg = "Target was cracked(success)"
        else:
            self.responce_msg = "Target was not reached"
            if not request_started:
                self.responce_msg = "Request was not started"
            elif request_failed:
                # Request failed, responce should be exception.
                self.responce_msg = str(self.responce)
            elif client_errors:
                self.responce_msg = "Client experienced errors"
            else:
                err_msg = "Target not reached for unknown reasons"
                raise Exception(err_msg)


    async def isconfused(self):
        # Returns True the object is aware of state of responce
        results = any([
            await self.errors(),
            await self.failure(),
            await self.success()
        ])
        return not results

    async def confused_action(self):
        err_msg = f'''
        Not sure if attack failed or was success(confused)

        Record/Data: {self.data}
        Target Reached: {await self.target_reached()}
        Errors: {await self.errors()}
        Failed: {await self.failure()}
        Success: {await self.success()}
        '''
        raise Exception(err_msg)   


    async def start_until_target_reached(self):
        # Starts requests until target is reached
        # No need to retry if running until
        self._retries = 0
        while True:
            await self._start()
            await asyncio.sleep(self._retry_sleep_time)
            if await self.target_reached():
                break

    async def target_not_reached_action(self):
        # Method called if target is not reached
        # self._retries_started prevents recursion
        if not self._retries_started:
            self._retries_started = True
            for _ in range(self._retries):
                await self.start()
                time.sleep(self._retry_sleep_time)
                if await self.target_reached():
                    break


    async def after_request(self):
        # Called after start() completes
        await super().after_request()
        await self._validate_attack()
        await self._update_responce_message()
        if await self.isconfused():
            await self.confused_action()
        if not await self.target_reached():
            await self.target_not_reached_action()


    async def start(self):
        if self._request_until:
            self._request_until = False
            await self.start_until_target_reached()
            self._request_until = True
        else:
            await super().start()



class AttackTextAsync(AttackAsync, BytesCompare):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        BytesCompare.__init__(self, b"")
        super().__init__(target, data, retries)

    async def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    async def success(self) -> bool:
        return BytesCompare.success(self)

    async def failure(self) -> bool:
        return BytesCompare.failure(self)

    async def target_errors(self) -> bool:
        return BytesCompare.target_error(self)

    async def client_errors(self) -> bool:
        if await super().client_errors():
            return True
        return BytesCompare.target_error(self)

    async def errors(self) -> bool:
        if await super().errors():
            return True
        return BytesCompare.error(self)   

    async def after_request(self):
        # Careful of when to call super().after_request()
        responce_content = await self.responce_content()
        responce_bytes = self._create_responce_bytes(responce_content)
        self._responce_bytes = responce_bytes
        await super().after_request()
