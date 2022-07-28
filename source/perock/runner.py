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
from typing import Type

from . import attack
from . import bforce
from . import forcetable


class RunnerBase():
    '''Base class for running bruteforce attack on target'''
    def __init__(self, 
    attack_class: Type[attack.Attack], 
    bforce_class: bforce.BForceBase) -> None:
        self._attack_class = attack_class
        self._bforce_class = bforce_class
        self._bforce: bforce_class

        self._target = None
        self._table: forcetable.Table = None

        self._optimise = True
        self._cancel_immediately = False
        self._max_success_records: int = None

        self._max_parallel_primary_tasks: int = None
        self._success_records = list()

    def set_target(self, target):
        '''Sets target/pointer to target to use for attack'''
        self._target = target
    
    def set_table(self, table):
        '''Sets table object with records for attack'''
        if not isinstance(table, forcetable.Table):
            err_msg = "table needs to instance of Table class not" +\
            " " + str(type(table))
            raise TypeError(err_msg)
        self._table = table

    def enable_optimise(self):
        '''Enables optimisations(requires primary column)'''
        self._optimise = True

    def disable_optimise(self):
        '''Disables optimisations(primary column not required)'''
        self._optimise = False

    def enable_cancel_immediately(self):
        '''Enables cancelling of tasks on first success'''
        self._cancel_immediately = True

    def disable_cancel_immediately(self):
        '''Disables cancelling of tasks on first success'''
        self._cancel_immediately = False

    def set_max_success_records(self, total):
        '''Sets maximum success records to cancel/stop attack'''
        self._max_success_records = total

    def set_max_parallel_primary_tasks(self, total):
        '''Set maxumum primary items to execute in parrallel'''
        self._max_parallel_primary_tasks = total

    def get_success_records(self):
        '''Returns records that were cracked/successful'''
        return self._success_records

    def get_cracked_records(self):
        '''Returns records that were cracked/successful'''
        return self.get_success_records()

    def _create_bforce_object(self):
        if self._target == None:
            err_msg = "Target is missing or None"
            raise Exception(err_msg)
        if self._table == None:
            err_msg = "Table is missing or None"
            raise Exception(err_msg)

        bforce = self._bforce_class(
            self._target, self._table, self._optimise
        )
        bforce.set_attack_class(self._attack_class)
        return bforce

    def _after_create_bforce_object(self):
        # Method is called after creating bforce object
        # Its safe to access self._bforce
        # This method body sets/updates attributes of self._bforce
        if self._max_parallel_primary_tasks != None:
            self._bforce.set_max_parallel_primary_tasks(
                self._max_parallel_primary_tasks
            )

        if self._cancel_immediately != None:
            if self._cancel_immediately:
                self._bforce.enable_cancel_immediately()
            else:
                self._bforce.disable_cancel_immediately()
        if self._max_success_records != None:
            self._bforce.set_max_success_records(self._max_success_records)

    def _setup_before_object(self):
        # Setup bforce object to use with nunner
        self._bforce = self._create_bforce_object()
        self._after_create_bforce_object()

    def _after_attack(self):
        # Method called after self.start() completes
        self._success_records = self._bforce.get_success_records()


    def start(self):
        self._setup_before_object()
        self._bforce.start()
        self._after_attack()

    def run(self):
        '''Entry point to starting attack on target'''
        self.start()


class RunnerParallel(RunnerBase):
    '''Base class for running bruteforce attack in parallel'''
    def __init__(
        self, 
        attack_class: Type[attack.Attack], 
        bforce_class: bforce.BForceBase) -> None:
        super().__init__(attack_class, bforce_class)
        self._max_parallel_tasks: int = None
        self._max_workers: int = None

    def set_max_parallel_tasks(self, total_tasks: int):
        '''Sets maximum number of tasks to run in parallel'''
        self._max_parallel_tasks = total_tasks

    def set_max_workers(self, max_workers: int):
        '''Sets maximum workers to use to execute tasks in parallel'''
        self._max_workers = max_workers

    def _after_create_bforce_object(self):
        super()._after_create_bforce_object()
        if self._max_workers != None:
            self._bforce.set_max_workers(self._max_workers)
        if self._max_parallel_tasks != None:
            self._bforce.set_max_parallel_tasks(self._max_parallel_tasks)


class RunnerExecutor(RunnerParallel):
    '''Runs bruteforce attack on parallel using executor'''
    def __init__(
        self, 
        attack_class: Type[attack.Attack], 
        bforce_class: bforce.BForceBase) -> None:
        super().__init__(attack_class, bforce_class)
        self._executor: futures.Executor = None

    def set_executor(self, executor):
        '''Sets executor to use to execute tasks'''
        self._executor = executor

    def _after_create_bforce_object(self):
        super()._after_create_bforce_object()
        if self._executor != None:
            self._bforce.set_executor(self._executor)


class RunnerThread(RunnerExecutor):
    '''Runs bruteforce attack using threads'''
    def __init__(
        self, 
        attack_class: Type[attack.Attack], 
        bforce_class=bforce.BForceThread) -> None:
        super().__init__(attack_class, bforce_class)


# class RunnerProcess(RunnerExecutor):
#     '''Runs bruteforce attack using multi-proccessing'''
#     def __init__(
#         self, 
#         attack_class: Type[attack.Attack], 
#         bforce_class=bforce.BForceProcess) -> None:
#         super().__init__(attack_class, bforce_class)


class RunnerAsync(RunnerParallel):
    '''Runs bruteforce attack on target using asyncio'''
    def __init__(self, 
    attack_class: Type[attack.AttackAsync], 
    bforce_class=bforce.BForceAsync) -> None:
        super().__init__(attack_class, bforce_class)

    async def start(self):
        self._setup_before_object()
        await self._bforce.start()
        self._after_attack()

    async def run(self):
        await self.start()


class RunnerBlock(RunnerBase):
    '''Runs bruteforce attack on target synchronously(blocking)'''
    def __init__(self, 
    attack_class: Type[attack.Attack], 
    bforce_class=bforce.BForceBlock) -> None:
        super().__init__(attack_class, bforce_class)


class Runner(RunnerThread):
    '''High level runner for running bruteforce likely using threads
    
    Its reccommended to use RunnerThread instead of this class for
    bruteforce using thread. Its not guaranteed that it will always
    use threads, it may be changed to use something else.'''

    def __init__(self, attack_class: Type[attack.Attack]) -> None:
        super().__init__(attack_class)


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
    runner.set_max_parallel_primary_tasks(10)
    asyncio.run(runner.run())
