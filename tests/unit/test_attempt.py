import unittest
import aiounittest

from perock.attempt import Attempt
from perock.attempt import AttemptAsync

from perock.target import Target
from perock.target import Account

from .common_classes import Session
from .common_classes import Responce


class SampleAttempt(Attempt):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self._target: Target
        self.request_should_fail = False
    
    def request(self):
        if not self.request_should_fail:
            account = Account(self._data)
            return self._target.login(account)
        else:
            return Exception()

    def set_responce(self, responce):
        self._responce = responce

    @classmethod
    def close_session(cls, session):
        session.close()

    @classmethod
    def close_responce(cls, session):
        session.close()


class SampleAttemptAsync(AttemptAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self._target: Target
        self.request_should_fail = False
    
    async def request(self):
        if not self.request_should_fail:
            account = Account(self._data)
            return self._target.login(account)
        else:
            return Exception()

    def set_responce(self, responce):
        self._responce = responce

    @classmethod
    async def close_session(cls, session):
        session.close()

    @classmethod
    async def close_responce(cls, session):
        session.close()


class TestAttemptSetUp():
    def setUp(self):
        # Prapares data to use with attack objects
        self._data = {"username": "Marry", "password": "oo.232.4"}
        self.data2 = {"username": "Berry", "password": "3khd53"}
        self.data3 = "Marry"

        # Prepares target to use with attack
        self._target = Target()
        self.account = Account(self._data)
        self._target.add_account(self.account)

        # Fake session and responce
        self._session = Session()
        self._responce = Responce()

        # Initialise attack objects
        self.create_attempt_objects()

    def create_attempt_objects(self):
        # Initialise attack objects
        self.attempt = SampleAttempt(self._target, self._data)
        self.attempt2 = SampleAttempt(self._target, self.data2)
        self.attempt3 = SampleAttempt(self._target, self.data3)



class TestAttemptSetUpAsync(TestAttemptSetUp):
    def create_attempt_objects(self):
        # Initialise attack objects
        self.attempt = SampleAttemptAsync(self._target, self._data)
        self.attempt2 = SampleAttemptAsync(self._target, self.data2)
        self.attempt3 = SampleAttemptAsync(self._target, self.data3)


class TestAttemptCommon(TestAttemptSetUp):
    def test_create_session(self):
        with self.assertRaises(NotImplementedError):
            self.attempt.create_session()

    def test_close_session(self):
        self.attempt.close_session(self._session)
        self.assertTrue(self._session.closed)

    def test_close_responce(self):
        self.attempt.close_responce(self._responce)
        self.assertTrue(self._responce.closed)
        

    def test_set_session(self):
        self.attempt.set_session(self._session)
        self.assertEqual(self.attempt.get_session(), self._session)

    def test_get_session(self):
        self.assertEqual(self.attempt.get_session(), None)
        self.attempt.set_session(self._session)
        self.assertEqual(self.attempt.get_session(), self._session)

    def test_get_responce(self):
        # No responce as there was no request
        self.assertEqual(self.attempt.get_responce(), None)
        
        # Starts request
        self.attempt.start()

        # Gets responce messages fro responce objects
        responce_message = self.attempt.request().get_message()
        responce2_message = self._target.login(self.account).get_message()
        # Test if the responce message are equal
        self.assertEqual(responce_message, responce2_message)

    def test_request(self):
        # Gets responce messages fro responce objects
        responce_message = self.attempt.request().get_message()
        responce2_message = self._target.login(self.account).get_message()

        self.assertEqual(responce_message, responce2_message)
        self.attempt.request_should_fail = True
        responce = self.attempt.request()
        self.assertIsInstance(responce, Exception)


    def before_request(self):
        # Harder to test
        self.attempt.after_request()

    def test_after_request(self):
        # Harder to test
        self.attempt.after_request()

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
        await self.attempt.close_session(self._session)
        self.assertTrue(self._session.closed)

    async def test_close_responce(self):
        await self.attempt.close_responce(self._responce)
        self.assertTrue(self._responce.closed)

    async def test_get_responce(self):
        # No responce as there was no request
        self.assertEqual(self.attempt.get_responce(), None)
        
        # Starts request
        await self.attempt.start()

        # Gets responce messages fro responce objects
        responce = await self.attempt.request()
        responce_msg = responce.get_message()
        responce2 = self._target.login(self.account)
        responce2_msg = responce2.get_message()

        # Test if the responce message are equal
        self.assertEqual(responce_msg, responce2_msg)


    async def before_request(self):
        await self.attempt.after_request()

    async def test_after_request(self):
        await self.attempt.after_request()

    async def test_request(self):
        # Gets responce messages from responce objects
        responce = await self.attempt.request()
        responce_msg = responce.get_message()
        responce2 = self._target.login(self.account)
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

class TestAttemptAsync(TestAttemptAsyncCommon, aiounittest.AsyncTestCase):
    pass

