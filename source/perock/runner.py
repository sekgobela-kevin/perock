'''
Starts and runs bruteforce attack on target with specied Attack and 
BForce class.

The module defines two(2) classes being Runner and RunnerAsync.
Runner can be used for asynchronous and threaded execution while
RunnerAsync is for asynchronous version of Runner class which
has methods that take long to finish being async/coroutine.

The module aims to simplify 'bforce' module similar to 'brutoforce'
module. Checkout 'brutoforce' module which uses different way of 
simplifying 'bforce' module.

Author: Sekgobela Kevin
Date: July 2022
Languages: Python 3
'''
from concurrent import futures
import typing
import time

from . import attack
from . import bforce
from . import forcetable


class RunnerBase():
    '''Base class for running bruteforce attack on target'''
    _bforce_type = bforce.BForceBase

    def __init__(self, 
    attack_class: typing.Type[attack.Attack], 
    target: typing.Any,
    table: forcetable.Table,
    optimise = False) -> None:
        self._runner_start_time = 0
        self._runner_end_time = 0
        self._bforce = self._bforce_type(target, table, optimise)
        self._bforce.set_attack_class(attack_class)

    def _update_runner_start_time(self):
        # Updates start time of runner
        self._runner_start_time = time.time()

    def _update_runner_end_time(self):
        # Updates start time of runner
        self._runner_end_time = time.time()

    def set_start_callback(self, callback):
        '''Sets function to be called at start of bruteforce session'''
        self._bforce.set_start_callback(callback)

    def set_done_callback(self, callback):
        '''Sets function to be called when bruteforce completes'''
        self._bforce.set_done_callback(callback)

    def set_switch_callback(self, callback):
        '''Sets function to be called when switching primary records
        
        Function is expected to accept single argument being record.
        Realise that record can be None which means primary records reached
        the end due to all of them being used.'''
        self._bforce.set_producer_switch_callback(callback)

    def enable_optimise(self):
        '''Enables optimisations(requires primary column)'''
        self._bforce.enable_optimise()

    def disable_optimise(self):
        '''Disables optimisations(primary column not required)'''
        self._bforce.disable_optimise()

    def enable_cancel_immediately(self):
        '''Enables cancelling of tasks on first success'''
        self._bforce.enable_cancel_immediately()

    def disable_cancel_immediately(self):
        '''Disables cancelling of tasks on first success'''
        self._bforce.disable_cancel_immediately()

    def set_max_success_records(self, total):
        '''Sets maximum success records to cancel/stop attack'''
        self._bforce.set_max_success_records(total)

    def set_max_multiple_primary_items(self, total):
        '''Set maximum primary items to execute in parrallel'''
        self._bforce.set_max_multiple_primary_items(total)

    def set_max_success_primary_items(self, total):
        '''Set maximum primary items with success record'''
        self._bforce.set_max_success_primary_items(total)
    
    def set_max_primary_item_success_records(self, total):
        '''Set maximum success records for each primary item'''
        self._bforce.set_max_primary_item_success_records(total)

    def add_excluded_primary_items(self, primary_item):
        '''Adds primary field item to be excluded'''
        self._bforce.add_excluded_primary_items(primary_item)

    def remove_excluded_primary_items(self, primary_item):
        '''Removes primary field item from excluded primary field'''
        self._bforce.remove_excluded_primary_items(primary_item)


    def get_excluded_primary_items(self):
        '''Gets excluded primary field items'''
        return self._bforce.get_excluded_primary_items()

    def get_table(self):
        '''Gets table with records to bruteforce.'''
        return self._bforce.get_table()

    def is_primary_optimised(self):
        '''Checks primary optimations are enabled.'''
        return self._bforce.is_primary_optimised()

    def session_exists(self):
        '''Checks if session exists'''
        return self._bforce.session_exists()

    def set_session(self, session):
        '''Sets session object to be used with runner'''
        return self._bforce.set_session(session)

    def get_session(self):
        '''Gets session object used by runner'''
        return self._bforce.get_session()

    def create_session(self, *args, **kwargs):
        '''Create session exatly as runner would create it'''
        return self._bforce.create_session(*args, **kwargs)

    def get_success_records(self):
        '''Returns records that were cracked/successful'''
        return self._bforce.get_success_records()

    def get_cracked_records(self):
        '''Returns records that were cracked/successful'''
        return self.get_success_records()

    def get_runner_time(self):
        '''Gets elapsed time of runner'''
        return self._runner_end_time - self._runner_start_time

    def is_running(self):
        '''Checks if runner is currently running'''
        return self._bforce.running()

    def started(self):
        '''Checks if runner if runner was ever started running'''
        return self._runner_start_time > 0 or self.is_running()

    def completed(self):
        '''Checks if runner if runner completed running'''
        return self.started() and not self.is_running()

    def stop(self):
        '''Stops runner and terminate any pending records.'''
        self._bforce.cancel()

    def start(self):
        self._update_runner_start_time()
        self._bforce.start()
        self._update_runner_end_time()

    def run(self):
        '''Entry point to starting attack on target'''
        self.start()


class RunnerParallel(RunnerBase):
    '''Base class for running bruteforce attack in parallel'''
    _bforce_type = bforce.BForceParallel

    def set_max_parallel_tasks(self, total_tasks: int):
        '''Sets maximum number of tasks to run in parallel'''
        self._bforce.set_max_parallel_tasks(total_tasks)

    def set_max_workers(self, max_workers: int):
        '''Sets maximum workers to use to execute tasks in parallel'''
        self._bforce.set_max_workers(max_workers)


class RunnerExecutor(RunnerParallel):
    '''Runs bruteforce attack on parallel using executor'''
    _bforce_type = bforce.BForceExecutor

    def set_executor(self, executor):
        '''Sets executor to use to execute tasks'''
        self._bforce.set_executor(executor)


class RunnerThread(RunnerExecutor):
    '''Runs bruteforce attack using threads'''
    _bforce_type = bforce.BForceThread


# class RunnerProcess(RunnerExecutor):
#     '''Runs bruteforce attack using multi-proccessing'''
#     _bforce_type = bforce.BForceProcess

#     def __init__(
#         self, 
#         attack_class: typing.Type[attack.Attack], 
#         target: typing.Any, 
#         table: forcetable.Table, 
#         optimise=False) -> None:
#         super().__init__(attack_class, target, table, optimise)
#         self._bforce: bforce.BForceProcess

#     @property
#     def bforce_class(self):
#         # Refers to bforce class to be used by runner
#         return bforce.BForceProcess


class RunnerAsync(RunnerParallel):
    '''Runs bruteforce attack on target using asyncio'''
    _bforce_type = bforce.BForceAsync

    async def start(self):
        self._update_runner_start_time()
        await self._bforce.start()
        self._update_runner_end_time()

    async def run(self):
        await self.start()


class RunnerBlock(RunnerBase):
    '''Runs bruteforce attack on target synchronously(blocking)'''
    _bforce_type = bforce.BForceBlock


class Runner(RunnerThread):
    '''High level runner for running bruteforce likely using threads
    
    Its reccommended to use RunnerThread instead of this class for
    bruteforce using thread. Its not guaranteed that it will always
    use threads, it may be changed to use something else.'''
    pass


if __name__ == "__main__":
    import asyncio
    from .attacks import *

    usernames = ["Marry", "Bella", "Michael"]
    passwords = range(10000000)

    # Creates fields for table
    usernames_col = forcetable.Field('usernames', usernames)
    # Sets key name to use in record key in Table
    usernames_col.set_item_name("username")
    passwords_col = forcetable.Field('passwords', passwords)
    passwords_col.set_item_name("password")

    table = forcetable.Table()
    # Set common record to be shared by all records
    common_record = forcetable.Record()
    common_record.add_item("submit", "login")
    table.set_common_record(common_record)
    # Add fields to table
    table.add_primary_field(usernames_col)
    table.add_field(passwords_col)

    class AttackClass(TestAttackAsync):
        def __init__(self, target, data: dict, retries=1) -> None:
            super().__init__(target, data, retries)
            self.set_sleep_time(1)
            self.add_unraised_exception(Exception)

        async def success(self):
            return True

        async def failure(self):
            return False
    

    class WebAttackClass(WebAttackAsync):
        def __init__(self, target, data: dict, retries=1) -> None:
            super().__init__(target, data, retries)

        async def success(self):
            await self.target_reached()

        async def start(self):
            await super().start()



    runner = RunnerAsync(AttackClass)
    runner.set_target('https://example.com')
    runner.set_table(table)
    runner.disable_optimise()
    runner.enable_cancel_immediately()
    runner.set_max_parallel_tasks(1000)
    runner.set_max_multiple_primary_items(10)
    asyncio.run(runner.run())
