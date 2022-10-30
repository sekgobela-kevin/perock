'''
Communicates with target/system and also analyse responce on 
single attempt.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
import asyncio
import time 
import typing
import inspect

from . attempt import Attempt
from . attempt import AttemptAsync

from . check import Check
from . check import CheckAsync

from . responce import ResponceBytesAnalyser

from perock import exceptions 


class BaseAttack():
    '''Base class for attempting to log to target with data'''
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

        self._should_validate_attack = True
        self._should_update_responce_message = True

    def set_retries(self, retries):
        self._retries = retries

    def set_retries_sleep_time(self, seconds):
        self._retry_sleep_time = seconds

    @classmethod
    def _static_validate_response_results(
        cls,
        response,
        target_reached,
        request_failed,
        request_started,
        
        target_errors,
        client_errors,
        errors,

        failure,
        success
        ):
        # Validates response results(raises exceptions)
        main_results = [errors, success, failure]

        if not request_started:
            if target_reached:
                err_msg = "Target cant be reached while request " +\
                    "was not started"
                raise exceptions.UnexpectedResponseError(err_msg)
            if request_failed:
                err_msg = "Request cant fail if request was not started"
                raise exceptions.UnexpectedResponseError(err_msg)
            if any(main_results):
                err_msg = "errors, success or failure not expected if "
                "request was not started"
                raise exceptions.UnexpectedResponseError(err_msg)

        if request_failed:
            if not client_errors:
                err_msg = "Client error expected if request failed"
                raise exceptions.UnexpectedResponseError(err_msg)
            if target_errors:
                err_msg = "Target error not allowed if request failed"
                raise exceptions.UnexpectedResponseError(err_msg)

        if target_reached:
            if request_failed:
                err_msg = "Request cant fail if target was reached"
                raise exceptions.UnexpectedResponseError(err_msg)
            if client_errors:
                err_msg = "Client error not expected if target was reached"
                raise exceptions.UnexpectedResponseError(err_msg)
            if not (success or failure or target_errors):
                err_msg = "'success', 'failure' or 'target error' expected " +\
                "if target was reached"
                raise exceptions.UnexpectedResponseError(err_msg)

        if not target_reached:
            if target_errors:
                err_msg = "Target error not expected if target " +\
                    "was not reached"
                raise exceptions.UnexpectedResponseError(err_msg)
            if success:
                err_msg = "success not expected if target " +\
                    "was not reached"
                raise exceptions.UnexpectedResponseError(err_msg)
            if failure:
                err_msg = "failure not expected if target " +\
                    "was not reached"
                raise exceptions.UnexpectedResponseError(err_msg)
                    

        if errors and not (client_errors or target_errors):
            err_msg = "Error encounted but no client or target errors"
            raise exceptions.UnexpectedResponseError(err_msg)

        if success and failure:
            err_msg = "success and failure cant happen at the same time"
            raise exceptions.UnexpectedResponseError(err_msg)

        if errors and (success or failure):
            err_msg = "Error not expected if theres success or failure"
            raise exceptions.UnexpectedResponseError(err_msg)

        if not (errors or success or failure):
            err_msg = "Error, success or failure is expected"
            raise exceptions.UnexpectedResponseError(err_msg)

    @classmethod
    def _static_update_responce_message(        
        cls,
        response,
        target_reached,
        request_failed,
        request_started,
        
        target_errors,
        client_errors,
        errors,

        failure,
        success):   
        '''Updates response message based on arguments'''     
        if target_reached:
            responce_msg = "Target was reached"
            if target_errors:
                responce_msg = "Target experienced errors"
            elif failure:
                responce_msg = "Failed to crack target(failure)"
            elif success:
                responce_msg = "Target was cracked(success)"
            else:
                responce_msg = "Target reached but confused"
        else:
            responce_msg = "Target was not reached"
            if not request_started:
                responce_msg = "Request was not started"
            elif request_failed:
                # Request failed, responce should be exception.
                responce_msg = str(response)
            elif client_errors:
                responce_msg = "Client experienced errors"
            else:
                responce_msg = "Target not reached for unknown reasons"
        return responce_msg

    @classmethod
    def static_isconfused(cls, error, failure, success):
        # Atleast success, error or failure is expected
        total_true = len(list(filter(None, [error, failure, success])))
        return total_true != 1

    @classmethod
    def static_confused_action(self, data, target_reached, error, failure, success):
        # Method called if theres is confusion
        err_msg = '''
        Something is wrong with response

        Record/Data: {data}
        Target Reached: {target_reached}
        Errors: {errors}
        Failed: {failure}
        Success: {success}
        '''
        err_msg = err_msg.format(
            data=data,
            target_reached=target_reached,
            errors=error,
            failure=failure,
            success=success,
        )
        raise exceptions.UnexpectedError(err_msg)   

    def create_results_map(self):
        '''Creates map with results from response'''
        return {
            "target_reached": self.target_reached(),
            "request_failed": self.request_failed(),
            "request_started": self.request_started(),

            "target_error": self.target_errors(),
            "client_error": self.client_errors(),
            "error": self.errors(),

            "failure": self.failure(),
            "success": self.success()
        }

    def _after_attack_checks(self, results_map):
        target_reached = results_map["target_reached"]
        request_failed = results_map["request_failed"]
        request_started = results_map["request_started"]

        target_errors = results_map["target_error"]
        client_errors = results_map["client_error"]
        errors = results_map["error"]

        failure = results_map["failure"]
        success = results_map["success"]
        if self._should_validate_attack:
            self._static_validate_response_results(
                response= self._responce,
                target_reached = target_reached,
                request_failed = request_failed,
                request_started = request_started,

                target_errors = target_errors,
                client_errors = client_errors,
                errors = errors,

                failure = failure,
                success = success)
        
        if self._should_update_responce_message:
            self._responce_msg = self._static_update_responce_message(
                response= self._responce,
                target_reached = target_reached,
                request_failed = request_failed,
                request_started = request_started,

                target_errors = target_errors,
                client_errors = client_errors,
                errors = errors,

                failure = failure,
                success = success)  


        if self.static_isconfused(errors, failure, success):
            self.static_confused_action(
                data=self._data,
                target_reached=target_reached, 
                error=errors, 
                failure=failure, 
                success=success
            )


class Attack(BaseAttack, Attempt, Check):
    '''Single attempt to logs into system with data'''
    base_attempt_class = Attempt
    base_check_class = Check

    def is_confused(self):
        '''Checks if respose results are unexpected'''
        results_map = self.create_results_map()
        return self.static_isconfused(
                error=results_map["error"], 
                failure=results_map["failure"], 
                success=results_map["success"]
            )
    
    def start_until_target_reached(
        self,
        should_continue_callaback = lambda : True):
        '''Starts attack infinitely until target is reached.

        should_continue_callaback: Callable
            Callable which if returns False stops the method
        '''
        while True:
            self.start()
            if self.target_reached():
                break
            elif not should_continue_callaback():
                break
            time.sleep(self._retry_sleep_time)

    def start_until_retries(
        self,
        should_continue_callaback = lambda : True):
        '''Starts requests for tries until target is reached

        should_continue_callaback: Callable
            Callable which if returns False stops the method'''
        for _ in range(self._tries):
            self.start()
            if self.target_reached():
                break
            elif not should_continue_callaback():
                break
            time.sleep(self._retry_sleep_time)

    def _after_request(self):
        # Called after start() completes
        super()._after_request()
        self._after_attack_checks(self.create_results_map())



class AttackAsync(BaseAttack, AttemptAsync, CheckAsync):
    '''Perform attack using request implemeted with asyncio'''
    base_attempt_class = AttemptAsync
    base_check_class = CheckAsync

    def __init__(self, target, data: dict, retries=1) -> None:
        self.base_attempt_class.__init__(self, target, data, retries)
        self.base_check_class.__init__(self, self)
        self._retries = 10
        self._tries = retries + 1
        self._retry_sleep_time = 0

        self._should_validate_attack = True
        self._should_update_responce_message = True


    async def start_until_target_reached(
        self,
        should_continue_callaback = lambda : True):
        '''Starts attack infinitely until target is reached
        should_continue_callaback: Callable
            Callable which if returns False stops the method
        '''
        while True:
            await self.start()
            if await self.target_reached():
                break
            elif not should_continue_callaback():
                break
            await asyncio.sleep(self._retry_sleep_time)

    async def start_until_retries(
        self,
        should_continue_callaback = lambda : True):
        '''Starts requests for tries until target is reached
        should_continue_callaback: Callable
            Callable which if returns False stops the method'''
        for _ in range(self._tries):
            await self.start()
            if await self.target_reached():
                break
            elif not should_continue_callaback():
                break
            await asyncio.sleep(self._retry_sleep_time)

    async def create_results_map(self):
        results_map = super().create_results_map()
        for name, method in results_map.items():
            if inspect.iscoroutine(method):
                value = await method
            else:
                value = method
            results_map[name] = value
        return results_map


    async def is_confused(self):
        '''Checks if respose results are unexpected'''
        results_map = await self.create_results_map()
        return self.static_isconfused(
                error=results_map["error"], 
                failure=results_map["failure"], 
                success=results_map["success"]
            )

    async def _after_request(self):
        # Called after start() completes
        await super()._after_request()
        results_map = await self.create_results_map()
        self._after_attack_checks(results_map)
        
