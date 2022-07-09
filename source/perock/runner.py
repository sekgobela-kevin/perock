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
from . import attack
from . import bforce
from . import forcetable


class Runner():
    def __init__(self, 
    attack_class=attack.Attack, 
    bforce_class=bforce.BForce) -> None:
        self._attack_class = attack_class
        self._bforce_class = bforce_class

        self._target = None
        self._table = None
        self._optimise = True

    def set_target(self, target):
        self._target = target
    
    def set_table(self, table):
        if not isinstance(table, forcetable.Table):
            err_msg = "table needs to instance of Table class not" +\
            " " + str(type(table))
            raise TypeError(err_msg)
        self._table = table

    def set_optimise(self):
        self._optimise = True

    def unset_optimise(self):
        self._optimise = False

    def _create_bforce_object(self):
        if self._target == None:
            err_msg = "Target is missing or None"
            raise Exception(err_msg)
        if self._table == None:
            err_msg = "Table is missing or None"
            raise Exception(err_msg)
        bforce = self._bforce_class(
            self._target, self._table, not self._optimise
        )
        bforce.set_attack_class(self._attack_class)
        return bforce

    def start(self):
        bforce_object = self._create_bforce_object()
        bforce_object.bforce.start()

    def run(self):
        self.start()


class RunnerAsync(Runner):
    def __init__(self, 
    attack_class=attack.AttackAsync, 
    bforce_class=bforce.BForceAsync) -> None:
        super().__init__(attack_class, bforce_class)

    async def start(self):
        bforce_object = self._create_bforce_object()
        await bforce_object.start()

    async def run(self):
        await self.start()



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

        async def request(self):
            self.ss


        @staticmethod
        async def create_session():
            import random 
            return "Session in string" + str(random.randint(0, 3000))


        def success(self):
            print(self.session)
            return True


    class WebAttackClass(WebAttackAsync):
        def __init__(self, target, data: dict, retries=1) -> None:
            super().__init__(target, data, retries)

        async def request(self):
            super().request()

        def success(self):
            print(asyncio.wait([self.text]))
            return self.target_reached()

        async def start(self):
            super().start_request()



    runner = RunnerAsync(WebAttackClass)
    runner.set_target('https://example.com')
    runner.set_table(table)
    runner.set_optimise()
    asyncio.run(runner.run())
