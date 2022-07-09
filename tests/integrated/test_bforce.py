import unittest

from common_classes import AttackSample
from common_test import CommonTest

from perock.target import Account
from perock.target import Target

from perock.forcetable import Table

import perock
from perock import target


class BForceTestTarget(target.Target):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        #self.set_responce_time(1)


class BForceCommonTest(CommonTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create passwords and usernames fields
        cls.usernames_field = perock.FieldFile("usernames", cls.usernames_file_path)
        cls.passwords_field = perock.FieldFile("passwords", cls.passwords_file_path)

        # Set items name 
        cls.usernames_field.set_item_name("username")
        cls.passwords_field.set_item_name("password")

    
    def setUp(self):
        super().setUp()
        # Create Ftable object
        self.setup_table()

        self.setup_target()

        self.setup_bforce_object()

        #attack = AttackSample(self.target, {"username":"THOMAS", "password":"marian"})
        #assert attack.success(), "Attack should be success"

    def setup_table(self):
        self.table = Table()
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
        self.bforce = perock.BForce(self.target, self.table)
        self.bforce.set_attack_class(AttackSample)

    def start(self):
        # Calls .start() of bforce object
        self.bforce.start()



    def test_start_loop_all(self):
        self.bforce.set_current_producer("loop_all")
        self.start()
        self.assertCountEqual(self.bforce.get_success_records(), self.accounts)

    def test_start_loop_some(self):
        self.bforce.set_current_producer("loop_some")
        self.start()
        self.assertCountEqual(self.bforce.get_success_records(), self.accounts)

    @classmethod
    def tearDownClass(cls):
        cls.usernames_field.close()
        cls.passwords_field.close()
     

class BForceTest(BForceCommonTest, unittest.TestCase):
    pass