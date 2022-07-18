import unittest
import asyncio

from common_classes import AttackSample
from common_classes import AttackAsyncSample
from common_test import CommonTest

from perock.target import Account
from perock.target import Target

from perock.forcetable import Table
from perock.forcetable import FieldFile

from perock import bforce
from perock import target


class BForceTestTarget(target.Target):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        #self.set_responce_time(1)


class BForceSetUp(CommonTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create passwords and usernames fields
        cls.usernames_field = FieldFile("usernames", cls.usernames_file_path)
        cls.passwords_field = FieldFile("passwords", cls.passwords_file_path)

        # Set items name 
        cls.usernames_field.set_item_name("username")
        cls.passwords_field.set_item_name("password")

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

        self.bforce.set_max_parallel_primary_tasks(20)

        #attack = AttackSample(self.target, {"username":"THOMAS", "password":"marian"})
        #assert attack.success(), "Attack should be success"

    def setup_table(self):
        # enable_callable_product=False
        # Enables use of itertools.product() for cartesian product
        # It should be True if max_parallel_primary_tasks > 1
        self.table = Table(enable_callable_product=False)
        self.table.add_primary_field(self.usernames_field)
        self.table.add_field(self.passwords_field)


    def setup_target(self):
        # Setup Target object
        self.target = BForceTestTarget()
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


    def setup_bforce_object(self):
        self.bforce = bforce.BForce(self.target, self.table)
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



class BForceAsyncCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = bforce.BForceAsync(self.target, self.table)
        self.bforce.set_attack_class(AttackAsyncSample)

    def start(self):
        asyncio.run(self.bforce.start())



class BForceBockCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = bforce.BForceBlock(self.target, self.table)
        self.bforce.set_attack_class(AttackSample)



class BForceAsyncTest(BForceAsyncCommonTest, unittest.TestCase):
    pass

class BForceTest(BForceCommonTest, unittest.TestCase):
    pass

class BForceBlockTest(BForceCommonTest, unittest.TestCase):
    pass



if __name__ == '__main__':
    unittest.main()