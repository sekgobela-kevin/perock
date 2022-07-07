import unittest
import asyncio

from common_classes import *
from common_test import *

from perock import target
from perock.forcetable import FTable
import perock


class BForceTestTarget(target.Target):
    def __init__(self, accounts: Iterable[Account] = ...) -> None:
        super().__init__(accounts)
        self.set_responce_time(1)


class BForceTest(CommonTest, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create passwords and usernames columns
        cls.usernames_column = perock.FColumnFile("usernames", cls.usernames_file_path)
        cls.passwords_column = perock.FColumnFile("passwords", cls.passwords_file_path)

        # Set items name 
        cls.usernames_column.set_item_name("username")
        cls.passwords_column.set_item_name("password")

    
    def setUp(self):
        super().setUp()
        # Create Ftable object
        self.ftable = FTable()
        self.ftable.add_primary_column(self.usernames_column)
        self.ftable.add_column(self.passwords_column)

        # Setup Target object
        self.target = Target()
        self.target_usernames = {
            "BROWN", "MARTINEZ", "ANDERSON", "THOMAS", "JACKSON"
        }
        self.target_passwords = {
            "1111111111", "kittycat", "ultimate", "marian", "vivian"
        }

        self.accounts = [
            Account({"username":"BROWN", "password":"1029384756"}),
            Account({"username":"MARTINEZ", "password":"bigboss"}),
            Account({"username":"ANDERSON", "password":"shuttle"}),
            Account({"username":"THOMAS", "password":"titanium"}),
            Account({"username":"JACKSON", "password":"underdog"})
        ]
        self.target.add_accounts(self.accounts)

        self.attack_class = AttackSample
        self.attack_async_class = AttackAsyncSample

        self.bforce = perock.BForce(self.target, self.ftable)
        self.bforce.set_attack_class(self.attack_class)

        self.bforce_async = perock.BForceAsync(self.target, self.ftable)
        self.bforce_async.set_attack_class(self.attack_async_class)

        self.bforce_block = perock.BForceBlock(self.target, self.ftable)
        self.bforce_block.set_attack_class(self.attack_class)
        #attack = AttackSample(self.target, {"username":"THOMAS", "password":"marian"})
        #assert attack.success(), "Attack should be success"

    def test_start(self):
        self.bforce.set_current_producer("loop_all")
        self.bforce.start()
        self.assertCountEqual(self.bforce.get_success_frows(), self.accounts)

    def test_start_async(self):
        self.bforce_async.set_current_producer("loop_all")
        asyncio.run(self.bforce_async.start())
        self.assertCountEqual(self.bforce_async.get_success_frows(), 
        self.accounts)

    def test_start_block(self):
        self.bforce_block.set_current_producer("loop_all")
        self.bforce_block.start()
        self.assertCountEqual(self.bforce_block.get_success_frows(), 
        self.accounts)

    def test_start_loop_some(self):
        self.bforce.set_current_producer("loop_some")
        self.bforce.start()
        self.assertCountEqual(self.bforce.get_success_frows(), self.accounts)

    @classmethod
    def tearDownClass(cls):
        cls.usernames_column.close()
        cls.passwords_column.close()
     