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

from .responce import ResponceBytesAnalyser


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
        self._tries = retries + 1
        self._retry_sleep_time = 0

    def set_retries(self, retries):
        self._retries = retries

    def set_retries_sleep_time(self, seconds):
        self._retry_sleep_time = seconds

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
            if not isinstance(self._responce, Exception):
                err_msg = "Responce should be exception if request failed"
                raise Exception(err_msg, type(self._responce))
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
            if len(list(filter(None, main_results))) != 1:
                true_filtered = list(filter(None, main_results))
                if len(true_filtered) == 0:
                    err_msg = "'success', 'failure' or 'errors' expected " +\
                    "if target was reached"
                else:
                    err_msg = "Only 1 between 'success', 'failure' " +\
                    "and 'errors' is expected if target was reached, " +\
                    "not " + str(len(true_filtered))
                raise Exception(err_msg)

        if not target_reached:
            if target_errors:
                err_msg = "Target error not expected if target was not reached"
                raise Exception(err_msg)
            if not client_errors:
                err_msg = "Client error expected if target was not reached"
                raise Exception(err_msg)
            if success and failure:
                err_msg = "success or failure not expected if target " +\
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
            self._responce_msg = "Target was reached"
            if self.target_errors():
                self._responce_msg = "Target experienced errors"
            elif self.failure():
                self._responce_msg = "Failed to crack target(failure)"
            elif self.success():
                self._responce_msg = "Target was cracked(success)"
        else:
            self._responce_msg = "Target was not reached"
            if not self.request_started():
                self._responce_msg = "Request was not started"
            elif self.request_failed():
                # Request failed, responce should be exception.
                self._responce_msg = str(self._responce)
            elif self.client_errors():
                self._responce_msg = "Client experienced errors"
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
        target_reached = self.target_reached()
        errors = self.errors()
        failure = self.failure()
        success = self.success()
        err_msg = '''
        Not sure if attack failed or was success(confused)

        Record/Data: {data}
        Target Reached: {target_reached}
        Errors: {errors}
        Failed: {failure}
        Success: {success}
        '''
        err_msg = err_msg.format(
            data=self._data,
            target_reached=target_reached,
            errors=errors,
            failure=failure,
            success=success,
        )
        raise Exception(err_msg)    

    def start_until_target_reached(self):
        # Starts requests infinitely until target is reached
        # No need to retry if running until
        while True:
            self.start()
            if self.target_reached():
                break
            time.sleep(self._retry_sleep_time)

    def start_for_tries(self):
        # Starts requests for tries until target is reached
        count = 0
        while count < self._tries:
            self.start()
            if self.target_reached():
                break
            time.sleep(self._retry_sleep_time)
            count += 1


    def target_not_reached_action(self):
        # Method called if target is not reached
        pass

    def after_request(self):
        # Called after start() completes
        super().after_request()
        self._validate_attack()
        self._update_responce_message()
        if not self.target_reached():
            self.target_not_reached_action()



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

    def set_retries(self, retries):
        self._retries = retries

    def set_retries_sleep_time(self, seconds):
        self._retry_sleep_time = seconds

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
            if not isinstance(self._responce, Exception):
                err_msg = "Responce should be exception if request failed"
                raise Exception(err_msg, type(self._responce))
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
            if len(list(filter(None, main_results))) != 1:
                true_filtered = list(filter(None, main_results))
                if len(true_filtered) == 0:
                    err_msg = "'success', 'failure' or 'errors' expected " +\
                    "if target was reached"
                else:
                    err_msg = "Only 1 between 'success', 'failure' " +\
                    "and 'errors' is expected if target was reached, " +\
                    "not " + str(len(true_filtered))
                raise Exception(err_msg)

        if not target_reached:
            if target_errors:
                err_msg = "Target error not expected if target was not reached"
                raise Exception(err_msg)
            if not client_errors:
                err_msg = "Client error expected if target was not reached"
                raise Exception(err_msg)
            if success and failure:
                err_msg = "success or failure not expected if target " +\
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
            self._responce_msg = "Target was reached"
            if target_errors:
                self._responce_msg = "Target experienced errors"
            elif failure:
                self._responce_msg = "Failed to crack target(failure)"
            elif success:
                self._responce_msg = "Target was cracked(success)"
        else:
            self._responce_msg = "Target was not reached"
            if not request_started:
                self._responce_msg = "Request was not started"
            elif request_failed:
                # Request failed, responce should be exception.
                self._responce_msg = str(self._responce)
            elif client_errors:
                self._responce_msg = "Client experienced errors"
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
        target_reached = await self.target_reached()
        errors = await self.errors()
        failure = await self.failure()
        success = await self.success()
        err_msg = '''
        Not sure if attack failed or was success(confused)

        Record/Data: {data}
        Target Reached: {target_reached}
        Errors: {errors}
        Failed: {failure}
        Success: {success}
        '''
        err_msg = err_msg.format(
            data=self._data,
            target_reached=target_reached,
            errors=errors,
            failure=failure,
            success=success,
        )
        raise Exception(err_msg)   


    async def start_until_target_reached(self):
        # Starts requests infinitely until target is reached
        # No need to retry if running until
        while True:
            await self.start()
            if await self.target_reached():
                break
            await asyncio.sleep(self._retry_sleep_time)

    async def start_for_tries(self):
        # Starts requests for tries until target is reached
        count = 0
        while count < self._tries:
            await self.start()
            if await self.target_reached():
                break
            await asyncio.sleep(self._retry_sleep_time)
            count += 1


    async def target_not_reached_action(self):
        # Method called if target is not reached
        pass



    async def after_request(self):
        # Called after start() completes
        await super().after_request()
        await self._validate_attack()
        await self._update_responce_message()
        if not await self.target_reached():
            await self.target_not_reached_action()



# -----------------------------------------------
# Attack Text classes begin here
# -----------------------------------------------


class AttackResponceBytesAnalyser():
    #ResponceBytesAnalyser class for attack text classes including 
    # AttackBytesAsync'''

    # This class is meant to be used temporary until ResponceBytesAnalyser
    # class is used fully.
    # It only strips away unwanted functionality from ResponceBytesAnalyser
    # The functionalities are just not needed currently.

    # Sorry, I cant write unit-tests for this class.
    # ResponceBytesAnalyser already has tests that already tests everything.
    def __init__(self, bytes_string, contains_strict=False) -> None:
        self._responce_analyser = ResponceBytesAnalyser(
            bytes_string, 
            contains_strict
        )

    def set_target_reached_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_target_reached_bytes_strings(bytes_strings)

    def set_target_errors_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_target_error_bytes_strings(bytes_strings)

    def set_client_errors_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_client_error_bytes_strings(bytes_strings)

    def set_errors_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_error_bytes_strings(bytes_strings)

    def set_success_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_success_bytes_strings(bytes_strings)

    def set_failure_bytes_strings(self, bytes_strings):
        self._responce_analyser.set_failure_bytes_strings(bytes_strings)


class AttackBytes(Attack, AttackResponceBytesAnalyser):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        AttackResponceBytesAnalyser.__init__(self, b"")

    def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    def target_reached(self):
        if super().target_reached():
            return True
        return self._responce_analyser.target_reached()

    def success(self) -> bool:
        return self._responce_analyser.success()

    def failure(self) -> bool:
        return self._responce_analyser.failure()

    def target_errors(self) -> bool:
        return self._responce_analyser.target_error()

    def client_errors(self) -> bool:
        if super().client_errors():
            return True
        return self._responce_analyser.target_error()

    def errors(self) -> bool:
        if super().errors():
            return True
        return self._responce_analyser.error()       

    def after_request(self):
        # Careful of when to call super().after_request()
        bytes_string = self.responce_content()
        self._responce_analyser.update(bytes_string)
        super().after_request()


class AttackBytesAsync(AttackAsync,  AttackResponceBytesAnalyser):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        AttackResponceBytesAnalyser.__init__(self, b"")

    async def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    async def target_reached(self):
        if await super().target_reached():
            return True
        return self._responce_analyser.target_reached()

    async def success(self) -> bool:
        return self._responce_analyser.success()

    async def failure(self) -> bool:
        return self._responce_analyser.failure()

    async def target_errors(self) -> bool:
        return self._responce_analyser.target_error()

    async def client_errors(self) -> bool:
        if await super().client_errors():
            return True
        return self._responce_analyser.target_error()

    async def errors(self) -> bool:
        if await super().errors():
            return True
        return self._responce_analyser.error()   

    async def after_request(self):
        # Careful of when to call super().after_request()
        bytes_string = await self.responce_content()
        self._responce_analyser.update(bytes_string)
        await super().after_request()
