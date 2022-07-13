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


class Runner():
    '''Runs bruteforce attack on target using threads'''
    def __init__(self, 
    attack_class: Type[attack.Attack], 
    bforce_class=bforce.BForce) -> None:
        self._attack_class = attack_class
        self._bforce_class = bforce_class

        self._target = None
        self._table: forcetable.Table = None

        self._optimise = True
        self._cancel_immediately = False
        self._max_success_records: int = None

        self._max_parallel_tasks: int = None
        self._max_parallel_primary_tasks: int = None
        self._max_workers: int = None

        self._executor: futures.Executor = None

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

    def set_max_parallel_tasks(self, total_tasks: int):
        '''Sets maximum number of tasks to run in parallel'''
        self._max_parallel_tasks = total_tasks

    def set_max_workers(self, max_workers: int):
        '''Sets maximum workers to use to execute tasks in parallel'''
        self._max_workers = max_workers

    def set_executor(self, executor):
        '''Sets executor to use to execute tasks'''
        self._executor = executor

    def set_max_parallel_primary_tasks(self, total):
        self._max_parallel_primary_tasks = total

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

        # Now the object is created
        # Its time to set some attributes on it
        # But should set them only when neccessay
        if self._max_workers != None:
            bforce.set_max_workers(self._max_workers)
        if self._max_parallel_tasks != None:
            bforce.set_max_parallel_tasks(self._max_parallel_tasks)
        if self._executor != None:
            bforce.set_executor(self._executor)
        if self._max_parallel_primary_tasks != None:
            bforce.set_max_parallel_primary_tasks(
                self._max_parallel_primary_tasks
            )

        # What should happen if _cancel_immediately and _max_success_records
        # are being set?
        # I guess _cancel_immediately imediately will take precidence.
        # Disabling _cancel_immediately shouldnt clear _max_success_records
        if self._cancel_immediately != None:
            if self._cancel_immediately:
                bforce.enable_cancel_immediately()
            else:
                bforce.disable_cancel_immediately()
        if self._max_success_records != None:
            bforce.set_max_success_records(self._max_success_records)
        return bforce


    def start(self):
        bforce_object = self._create_bforce_object()
        bforce_object.start()

    def run(self):
        '''Entry point to starting attack on target'''
        self.start()


class RunnerAsync(Runner):
    '''Runs bruteforce attack on target using asyncio'''
    def __init__(self, 
    attack_class: Type[attack.AttackAsync], 
    bforce_class=bforce.BForceAsync) -> None:
        super().__init__(attack_class, bforce_class)

    async def start(self):
        bforce_object = self._create_bforce_object()
        await bforce_object.start()

    async def run(self):
        await self.start()

class RunnerBlock(Runner):
    '''Runs bruteforce attack on target synchronously(blocking)'''
    def __init__(self, 
    attack_class: Type[attack.Attack], 
    bforce_class=bforce.BForceBlock) -> None:
        super().__init__(attack_class, bforce_class)




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
            await super().start_request()



    runner = RunnerAsync(AttackClass)
    runner.set_target('https://example.com')
    runner.set_table(table)
    runner.disable_optimise()
    runner.enable_cancel_immediately()
    runner.set_max_parallel_tasks(1000)
    runner.set_max_parallel_primary_tasks(10)
    asyncio.run(runner.run())
