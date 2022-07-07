import unittest
from .test_attempt import TestAttemptSetUp
from .test_attempt import TestAttemptSetUpAsync
from perock.check import Check


class TestCheckCommon(TestAttemptSetUp):
    def setUp(self):
        super().setUp()
        self.create_check_objects()
        self.check_start_request()


    def create_check_objects(self):
        # Initialises Check objects
        self.check = Check(self.attempt)
        self.check2 = Check(self.attempt2)
        self.check3 = Check(self.attempt3)

    def check_start_request(self):
        # Calls .start_request() of Attack objects
        # self.attack.start_request() would cause problems
        # if this class is inherited.
        self.check.get_attempt_object().start_request()
        self.check2.get_attempt_object().start_request()
        self.check3.get_attempt_object().request_should_fail = True
        self.check3.get_attempt_object().start_request()

    def test_get_attempt_object(self):
        self.assertEqual(self.check.get_attempt_object(), self.attempt)

    def test_success(self):
        with self.assertRaises(NotImplementedError):
            self.check.success()
        
    def test_target_errors(self):
        self.assertEqual(self.check.target_errors(), None)

    def test_client_errors(self):
        self.assertFalse(self.check.client_errors())
        self.assertTrue(self.check3.client_errors())

    def test_errors(self):
        self.assertFalse(self.check.errors())
        self.assertTrue(self.check3.errors())

    def test_responce_errors(self):
        self.assertFalse(self.check.responce_errors())
        self.assertFalse(self.check3.responce_errors())

class TestCheckAsyncCommon(TestAttemptSetUpAsync):
    pass



class TestCheck(TestCheckCommon, unittest.TestCase):
    pass


class TestCheck(TestCheckAsyncCommon, unittest.TestCase):
    pass