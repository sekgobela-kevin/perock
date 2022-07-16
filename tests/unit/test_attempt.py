import unittest
from unittest import IsolatedAsyncioTestCase

from perock.attempt import Attempt
from perock.attempt import AttemptAsync

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
            return Exception()

    def set_responce(self, responce):
        self.responce = responce


class SampleAttemptAsync(AttemptAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.target: Target
        self.request_should_fail = False
    
    async def request(self):
        if not self.request_should_fail:
            account = Account(self.data)
            return self.target.login(account)
        else:
            return Exception()

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
        self.create_attempt_objects()

    def create_attempt_objects(self):
        # Initialise attack objects
        self.attempt = SampleAttempt(self.target, self.data)
        self.attempt2 = SampleAttempt(self.target, self.data2)
        self.attempt3 = SampleAttempt(self.target, self.data3)



class TestAttemptSetUpAsync(TestAttemptSetUp):
    def create_attempt_objects(self):
        # Initialise attack objects
        self.attempt = SampleAttemptAsync(self.target, self.data)
        self.attempt2 = SampleAttemptAsync(self.target, self.data2)
        self.attempt3 = SampleAttemptAsync(self.target, self.data3)


class TestAttemptCommon(TestAttemptSetUp):
    def test_validate_data(self):
        self.assertTrue(self.attempt.validate_data(self.data))
        self.assertTrue(self.attempt.validate_data(self.data3))


    def test_create_session(self):
        with self.assertRaises(NotImplementedError):
            self.attempt.create_session()

    def test_close_session(self):
        self.attempt.set_session(self.session)
        self.attempt.close_session()
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
        # No responce as there was no request
        self.assertEqual(self.attempt.get_responce(), None)
        
        # Starts request
        self.attempt.start()

        # Gets responce messages fro responce objects
        responce_message = self.attempt.request().get_message()
        responce2_message = self.target.login(self.account).get_message()
        # Test if the responce message are equal
        self.assertEqual(responce_message, responce2_message)

    def test_request(self):
        # Gets responce messages fro responce objects
        responce_message = self.attempt.request().get_message()
        responce2_message = self.target.login(self.account).get_message()

        self.assertEqual(responce_message, responce2_message)
        self.attempt.request_should_fail = True
        responce = self.attempt.request()
        self.assertIsInstance(responce, Exception)


    def before_request(self):
        # Harder to test
        self.attempt.after_request()
        pass

    def test_after_request(self):
        # Harder to test
        self.attempt.after_request()
        pass

    def test_start(self):
        self.attempt.start()
        self.assertNotIsInstance(self.attempt.get_responce(), Exception)

        self.attempt.request_should_fail = True
        self.attempt.start()
        self.assertIsInstance(self.attempt.get_responce(), Exception)



class TestAttemptAsyncCommon(TestAttemptSetUpAsync, TestAttemptCommon):
    async def test_create_session(self):
        with self.assertRaises(NotImplementedError):
            await self.attempt.create_session()

    async def test_close_session(self):
        self.attempt.set_session(self.session)
        await self.attempt.close_session()
        self.assertTrue(self.session.closed)

    async def test_close_responce(self):
        self.attempt.set_responce(self.responce)
        await self.attempt.close_responce()
        self.assertTrue(self.responce.closed)

    async def test_get_responce(self):
        # No responce as there was no request
        self.assertEqual(self.attempt.get_responce(), None)
        
        # Starts request
        await self.attempt.start()

        # Gets responce messages fro responce objects
        responce = await self.attempt.request()
        responce_msg = responce.get_message()
        responce2 = self.target.login(self.account)
        responce2_msg = responce2.get_message()

        # Test if the responce message are equal
        self.assertEqual(responce_msg, responce2_msg)


    async def before_request(self):
        await self.attempt.after_request()

    async def test_after_request(self):
        await self.attempt.after_request()

    async def test_request(self):
        # Gets responce messages fro responce objects
        responce = await self.attempt.request()
        responce_msg = responce.get_message()
        responce2 = self.target.login(self.account)
        responce2_msg = responce2.get_message()

        self.assertEqual(responce_msg, responce2_msg)
        self.attempt.request_should_fail = True
        responce = await self.attempt.request()
        self.assertIsInstance(responce, Exception)

    async def test_start(self):
        await self.attempt.start()
        self.assertNotIsInstance(self.attempt.get_responce(), Exception)

        self.attempt.request_should_fail = True
        await self.attempt.start()
        self.assertIsInstance(self.attempt.get_responce(), Exception)



class TestAttempt(TestAttemptCommon, unittest.TestCase):
    pass

class TestAttemptAsync(TestAttemptAsyncCommon, IsolatedAsyncioTestCase):
    pass

