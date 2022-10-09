import unittest
import asyncio
from concurrent import futures

import aiounittest

from .common_classes import AttackSample
from .common_classes import AttackAsyncSample
from .common_test import CommonTest

from perock.target import Account
from perock.target import Target

from perock.forcetable import Table
from perock.forcetable import FieldFile

from perock import bforce
from perock import target


# Tests for this test module are based non IO blocking activity.
# It involves bruteforce with passwords and usernames from file system.
# Product of usernames and passwords is calculated.
# Each username-password combination is campared with other defined 
# username-password.

# There is no waiting, so there is no IO blocking activity taking place.
# BForceAsync and BForce are expected to perform slower than BForceBlock.
# BForceAsync and BForce were designed for IO blocking activity and 
# they will perform worst on CPU intensive activities.

# Setting ProccessPoolExecutor is failing as seen in the tests.
# BForceAsync and BForce will peform better on IO bound tasks such
# as performing internet request.


class BForceTestTarget(target.Target):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        #self.set_responce_time(1)


class BForceSetUp(CommonTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create passwords and usernames fields.
        # Set 'read_all' as True for file field if using multiple/parallel
        # primary items on bforce object.
        cls.usernames_field = FieldFile("usernames", cls.usernames_file_path,
        read_all=True)
        cls.passwords_field = FieldFile("passwords", cls.passwords_file_path,
        read_all=True)

        # Set items name 
        cls.usernames_field.set_item_name("username")
        cls.passwords_field.set_item_name("password")

        # Set executors
        cls.process_executor = futures.ProcessPoolExecutor()
        cls.thread_executor = futures.ThreadPoolExecutor()

    @classmethod
    def tearDownClass(cls):
        cls.usernames_field.close()
        cls.passwords_field.close()
    
    def setUp(self):
        super().setUp()
        # Create Ftable object
        self.setup_table()

        self.setup_target()

        self.setup_bforce_object()

        #attack = AttackSample(self._target, {"username":"THOMAS", "password":"marian"})
        #assert attack.success(), "Attack should be success"
        

    def setup_table(self):
        # enable_callable_product=False
        # Enables use of itertools.product() for cartesian product
        # It should be True if max_parallel_primary_tasks > 1
        self.table = Table()
        self.table.add_primary_field(self.usernames_field)
        self.table.add_field(self.passwords_field)


    def setup_target(self):
        # Setup Target object
        self._target = BForceTestTarget()
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
        self._target.add_accounts(self.accounts)


    def setup_bforce_object(self):
        self.bforce = bforce.BForce(self._target, self.table)
        self.bforce.set_attack_class(AttackSample)

    def start(self):
        # Calls .start() of bforce object
        self.bforce.start()


class BForceCommonTest(BForceSetUp):
    def test_start_not_optimised(self):
        self.bforce.disable_optimise()
        self.start()
        self.assertCountEqual(self.bforce.get_success_records(), self.accounts)

    def test_start_optimised(self):
        self.bforce.enable_optimise()
        self.start()
        self.assertCountEqual(self.bforce.get_success_records(), self.accounts)

    def test_parallel_primaty_tasks(self):        
        # This is not reccomended for file fields.
        # Set 'read_all' argument as True if using file field.
        self.bforce.set_max_parallel_primary_tasks(20)
        self.bforce.enable_optimise()
        self.start()
        self.assertCountEqual(self.bforce.get_success_records(), self.accounts)


class BForceAsyncCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = bforce.BForceAsync(self._target, self.table)
        self.bforce.set_attack_class(AttackAsyncSample)

    def start(self):
        # This is for supporting python 3.6
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.bforce.start())
        loop.close()



class BForceBlockCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = bforce.BForceBlock(self._target, self.table)
        self.bforce.set_attack_class(AttackSample)


class BForceThreadCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = bforce.BForceThread(self._target, self.table)
        self.bforce.set_attack_class(AttackSample)


class BForceTest(BForceCommonTest, unittest.TestCase):
    pass

class BForceBlockTest(BForceBlockCommonTest, unittest.TestCase):
    pass

class BForceAsyncTest(BForceAsyncCommonTest, aiounittest.AsyncTestCase):
    pass

class BForceThreadTest(BForceThreadCommonTest, unittest.TestCase):
    pass




if __name__ == '__main__':
    unittest.main()