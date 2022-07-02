import unittest

from perock.target import Responce
from perock.target import Account
from perock.target import Target

from .test_forcetable import TestFRowCommon


class TestResponceCommon():
    def setUp(self):
        self.message = "This is responce from target"
        self.message2 = "Second responce from target"

        self.status = 100
        self.status2 = 100

        self.responce = Responce(self.message, self.status)
        self.responce2 = Responce(self.message2, self.status2)


    def test_set_message(self):
        self.responce.set_message("message")
        self.assertEqual(self.responce.get_message(), "message")

    def test_get_message(self):
        self.assertEqual(self.responce.get_message(), self.message)

    def set_status(self, status):
        self.responce.set_status(500)
        self.assertEqual(self.responce.get_status(), 500)

    def get_status(self):
        self.assertEqual(self.responce.get_status(), 100)
    
    def test_close(self):
        self.assertFalse(self.responce.closed)
        self.responce.close()
        self.assertTrue(self.responce.closed)


class TestAccountCommon(TestFRowCommon):
    pass


class TestTargetCommon(unittest.TestCase):
    def setUp(self):
        # Create Account object
        self.account = Account()
        self.account.add_item("username", "Marry")
        self.account.add_item("password", ".234duct")

        # Creates another Account object
        self.account2 = Account()
        self.account2.add_item("username", "David")
        self.account2.add_item("password", "nhs149.89")

        # Create target and add account
        # self.account was not added
        self.target = Target()
        self.target.add_account(self.account)

        self.empty_target = Target()

    def test_set_responce_time(self):
        self.target.set_responce_time(10)
        self.assertEqual(self.target.get_responce_time(), 10)

    def test_get_responce_time(self):
        self.assertEqual(self.target.get_responce_time(), 0)

    def test_get_accounts(self):
        self.assertCountEqual(self.target.get_accounts(), [self.account])
        self.assertCountEqual(self.empty_target.get_accounts(), [])

    def test_add_account(self):
        self.empty_target.add_account(self.account)
        self.empty_target.add_account(self.account)
        self.assertIn(self.account, self.empty_target.get_accounts())
        # Duplicate accounts not allowed
        self.assertEqual(len(self.empty_target.get_accounts()), 1)

    def test_remove_account(self):
        self.target.remove_account(self.account)
        self.assertEqual(len(self.empty_target.get_accounts()), 0)

    def test_account_valid_form(self):
        self.assertTrue(self.target.account_valid_form(self.account))
        self.assertTrue(self.target.account_valid_form(self.account2))
        # Dictionary is not Account object
        self.assertFalse(self.target.account_valid_form(dict(self.account)))

    def test_account_exists(self):
        self.assertTrue(self.target.account_exists(self.account))
        self.assertFalse(self.target.account_exists(self.account2))


    def test_success_responce(self):
        responce = self.target.success_responce(self.account)
        self.assertEqual(responce.get_status(), 200)
        self.assertIn("unlocked", responce.get_message())

    def test_fail_responce(self):
        responce = self.target.fail_responce(self.account)
        self.assertEqual(responce.get_status(), 200)
        self.assertIn("Failed to log", responce.get_message())

    def test_access_denied_responce(self):
        responce = self.target.access_denied_responce(self.account)
        self.assertEqual(responce.get_status(), 403)
        self.assertIn("denied", responce.get_message())

    def test_target_error_responce(self):
        responce = self.target.target_error_responce(self.account)
        self.assertEqual(responce.get_status(), 500)
        self.assertIn("Our system", responce.get_message())

    def test_client_error_responce(self):
        responce = self.target.client_error_responce(self.account)
        self.assertEqual(responce.get_status(), 400)
        self.assertIn("your account", responce.get_message())

    def test_account_success(self):
        self.assertTrue(self.target.account_success(self.account))
        self.assertFalse(self.target.account_success(self.account2))

    def test_account_fail(self):
        self.assertFalse(self.target.account_fail(self.account))
        self.assertTrue(self.target.account_fail(self.account2))

    def test_target_error_detected(self):
        # .target_error_detected() always returns False
        self.assertFalse(self.target.target_error_detected(self.account2))

    def test_client_error_detected(self):
        self.assertFalse(self.target.client_error_detected(self.account))
        self.assertFalse(self.target.client_error_detected(self.account2))
        # String is not Account object
        self.assertTrue(self.target.client_error_detected("Marry"))

    def test_access_denied(self):
        self.assertFalse(self.target.access_denied(self.account))
        self.assertFalse(self.target.access_denied(self.account2))
        # String is not Account object(suspicious activity)
        self.assertTrue(self.target.access_denied("Marry"))


    def test_login(self):
        responce = self.target.login(self.account)
        self.assertIn("unlocked", responce.get_message())

        responce = self.target.login(self.account2)
        self.assertIn("Failed to log", responce.get_message())

        responce = self.target.login("Marry")
        self.assertIn("denied", responce.get_message())

        #responce = self.target.login("Marry")
        #self.assertIn("your account", responce.get_message())

        #responce = self.target.login(self.account)
        #self.assertIn("unlocked", responce.get_message())

        # Harder to test the .login() with other arguments
        # It would take inheritance of Target class
        # and redefining conditions




class TestAccount(TestAccountCommon, unittest.TestCase):
    pass


class TestResponce(TestResponceCommon, unittest.TestCase):
    pass