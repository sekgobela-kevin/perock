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

from . import attack
from . import bforce
from . import forcetable


class RunnerBase():
    '''Base class for running bruteforce attack on target'''
    def __init__(self, 
    attack_class: typing.Type[attack.Attack], 
    target: typing.Any,
    table: forcetable.Table,
    optimise = False) -> None:
        self._bforce = self.bforce_class(target, table, optimise)
        self._bforce.set_attack_class(attack_class)

    @property
    def bforce_class(self) -> typing.Type[bforce.BForceBase]:
        # Refers to bforce class to be used by runner
        raise NotImplementedError


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
        '''Set maxumum primary items to execute in parrallel'''
        self._bforce.set_max_multiple_primary_items(total)

    def get_success_records(self):
        '''Returns records that were cracked/successful'''
        return self._bforce.get_success_records()

    def get_cracked_records(self):
        '''Returns records that were cracked/successful'''
        return self.get_success_records()

    def start(self):
        self._bforce.start()

    def run(self):
        '''Entry point to starting attack on target'''
        self.start()


class RunnerParallel(RunnerBase):
    '''Base class for running bruteforce attack in parallel'''
    def __init__(
        self, 
        attack_class: typing.Type[attack.Attack], 
        target: typing.Any, 
        table: forcetable.Table, 
        optimise=False) -> None:
        super().__init__(attack_class, target, table, optimise)
        self._bforce: bforce.BForceParallel

    @property
    def bforce_class(self):
        # Refers to bforce class to be used by runner
        return bforce.BForceParallel

    def set_max_parallel_tasks(self, total_tasks: int):
        '''Sets maximum number of tasks to run in parallel'''
        self._bforce.set_max_parallel_tasks(total_tasks)

    def set_max_workers(self, max_workers: int):
        '''Sets maximum workers to use to execute tasks in parallel'''
        self._bforce.set_max_workers(max_workers)


class RunnerExecutor(RunnerParallel):
    '''Runs bruteforce attack on parallel using executor'''
    def __init__(
        self, 
        attack_class: typing.Type[attack.Attack], 
        target: typing.Any, 
        table: forcetable.Table, 
        optimise=False) -> None:
        super().__init__(attack_class, target, table, optimise)
        self._bforce: bforce.BForceExecutor

    @property
    def bforce_class(self):
        # Refers to bforce class to be used by runner
        return bforce.BForceExecutor

    def set_executor(self, executor):
        '''Sets executor to use to execute tasks'''
        self._bforce.set_executor(executor)


class RunnerThread(RunnerExecutor):
    '''Runs bruteforce attack using threads'''
    def __init__(
        self, 
        attack_class: typing.Type[attack.Attack], 
        target: typing.Any, 
        table: forcetable.Table, 
        optimise=False) -> None:
        super().__init__(attack_class, target, table, optimise)
        self._bforce: bforce.BForceThread

    @property
    def bforce_class(self):
        # Refers to bforce class to be used by runner
        return bforce.BForceThread


# class RunnerProcess(RunnerExecutor):
#     '''Runs bruteforce attack using multi-proccessing'''
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
    def __init__(
        self, 
        attack_class: typing.Type[attack.AttackAsync], 
        target: typing.Any, 
        table: forcetable.Table, 
        optimise=False) -> None:
        super().__init__(attack_class, target, table, optimise)
        self._bforce: bforce.BForceAsync

    @property
    def bforce_class(self):
        # Refers to bforce class to be used by runner
        return bforce.BForceAsync

    async def start(self):
        await self._bforce.start()

    async def run(self):
        await self.start()


class RunnerBlock(RunnerBase):
    '''Runs bruteforce attack on target synchronously(blocking)'''
    def __init__(
        self, 
        attack_class: typing.Type[attack.Attack], 
        target: typing.Any, 
        table: forcetable.Table, 
        optimise=False) -> None:
        super().__init__(attack_class, target, table, optimise)
        self._bforce: bforce.BForceBlock

    @property
    def bforce_class(self):
        # Refers to bforce class to be used by runner
        return bforce.BForceBlock


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
