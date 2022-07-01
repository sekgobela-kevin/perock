import unittest
from perock.attempt import Attempt
from perock.target import Target
from perock.target import Account

from .common_classes import Session
from .common_classes import Responce


class SampleAttempt(Attempt):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.target: Target
        self.request_should_fail = False
    
    def request(self):
        if not self.request_should_fail:
            account = Account(self.data)
            return self.target.login(account)
        else:
            return self.fail_responce

    def set_responce(self, responce):
        self.responce = responce


class TestAttemptSetUp():
    def setUp(self):
        # Prapares data to use with attack objects
        self.data = {"username": "Marry", "password": "oo.232.4"}
        self.data2 = {"username": "Berry", "password": "3khd53"}
        self.data3 = "Marry"

        # Prepares target to use with attack
        self.target = Target()
        self.account = Account(self.data)
        self.target.add_account(self.account)

        # Fake session and responce
        self.session = Session()
        self.responce = Responce()

        # Initialise attack objects
        self.attempt = SampleAttempt(self.target, self.data)
        self.attempt2 = SampleAttempt(self.target, self.data2)
        self.attempt3 = SampleAttempt(self.target, self.data3)


class TestAttemptCommon(TestAttemptSetUp):
    def test_validate_data(self):
        self.assertTrue(self.attempt.validate_data(self.data))
        self.assertTrue(self.attempt.validate_data(self.data3))


    def test_create_session(self):
        with self.assertRaises(NotImplementedError):
            self.attempt.create_session()

    def test_close_session(self):
        self.attempt.close_session(self.session)
        self.assertTrue(self.session.closed)

    def test_close_responce(self):
        self.attempt.set_responce(self.responce)
        self.attempt.close_responce()
        self.assertTrue(self.responce.closed)
        

    def test_set_session(self):
        self.attempt.set_session(self.session)
        self.assertEqual(self.attempt.get_session(), self.session)

    def test_get_session(self):
        self.assertEqual(self.attempt.get_session(), None)
        self.attempt.set_session(self.session)
        self.assertEqual(self.attempt.get_session(), self.session)

    def test_get_responce(self):
        self.assertEqual(self.attempt.get_responce(), None)
        self.attempt.start_request()
        self.assertEqual(self.attempt.get_responce(), 
            self.target.login(self.account)
        )

    def test_request(self):
        responce = self.attempt.request()
        self.assertEqual(responce, self.target.login(self.account))
        self.attempt.request_should_fail = True
        responce = self.attempt.request()
        self.assertEqual(responce, self.attempt.fail_responce)


    def before_start_request(self):
        # Harder to test
        pass

    def test_after_start_request(self):
        # Harder to test
        pass


    def test_request_failed(self):
        self.assertFalse(self.attempt.request_failed())
        self.attempt.start_request()
        self.assertFalse(self.attempt.request_failed())
        self.attempt.request_should_fail = True
        self.attempt.start_request()
        self.assertTrue(self.attempt.request_failed())


    def test_start_request(self):
        self.attempt.start_request()
        self.assertFalse(self.attempt.request_failed())
        self.assertTrue(self.attempt.target_reached())

        self.attempt.request_should_fail = True
        self.attempt.start_request()
        self.assertTrue(self.attempt.request_failed())
        self.assertFalse(self.attempt.target_reached())

    def test_target_reached(self):
        self.assertFalse(self.attempt.target_reached())
        self.attempt.start_request()
        self.assertTrue(self.attempt.target_reached())
        self.attempt.request_should_fail = True
        self.attempt.start_request()
        self.assertFalse(self.attempt.target_reached())


class TestAttempt(TestAttemptCommon, unittest.TestCase):
    pass

