import unittest

from common_classes import AttackSample
from common_test import CommonTest

from perock.target import Account
from perock.target import Target

from perock.forcetable import FTable

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
        # Create passwords and usernames columns
        cls.usernames_column = perock.FColumnFile("usernames", cls.usernames_file_path)
        cls.passwords_column = perock.FColumnFile("passwords", cls.passwords_file_path)

        # Set items name 
        cls.usernames_column.set_item_name("username")
        cls.passwords_column.set_item_name("password")

    
    def setUp(self):
        super().setUp()
        # Create Ftable object
        self.setup_ftable()

        self.setup_target()

        self.setup_bforce_object()

        #attack = AttackSample(self.target, {"username":"THOMAS", "password":"marian"})
        #assert attack.success(), "Attack should be success"

    def setup_ftable(self):
        self.ftable = FTable()
        self.ftable.add_primary_column(self.usernames_column)
        self.ftable.add_column(self.passwords_column)


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
        self.bforce = perock.BForce(self.target, self.ftable)
        self.bforce.set_attack_class(AttackSample)

    def start(self):
        # Calls .start() of bforce object
        self.bforce.start()



    def test_start_loop_all(self):
        self.bforce.set_current_producer("loop_all")
        self.start()
        self.assertCountEqual(self.bforce.get_success_frows(), self.accounts)

    def test_start_loop_some(self):
        self.bforce.set_current_producer("loop_some")
        self.start()
        self.assertCountEqual(self.bforce.get_success_frows(), self.accounts)

    @classmethod
    def tearDownClass(cls):
        cls.usernames_column.close()
        cls.passwords_column.close()
     

class BForceTest(BForceCommonTest, unittest.TestCase):
    pass