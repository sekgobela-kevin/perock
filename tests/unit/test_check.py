import unittest
from .test_attempt import TestAttemptSetUp
from perock.check import Check


class TestCheckCommon(TestAttemptSetUp):
    def setUp(self):
        super().setUp()
        self.attempt.start_request()
        self.attempt2.start_request()
        self.attempt3.request_should_fail = True
        self.attempt3.start_request()

        self.check = Check(self.attempt)
        self.check2 = Check(self.attempt2)
        self.check3 = Check(self.attempt3)

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


class TestCheck(TestCheckCommon, unittest.TestCase):
    pass