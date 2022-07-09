import asyncio
import unittest

from perock.attempt import AttemptAsync
from perock.target import *

from .test_attempt import TestAttemptSetUp
from .test_attempt import TestAttemptSetUpAsync

from perock.check import Check
from perock.check import CheckAsync


class CheckSample(Check):
    def __init__(self, attempt_object) -> None:
        super().__init__(attempt_object)

    def success(self):
        #responce: Responce
        responce = self._attempt_object.get_responce()
        if not self.errors():
            return "unlocked" in responce.get_message()


class CheckSampleAsync(CheckAsync):
    def __init__(self, attempt_object) -> None:
        super().__init__(attempt_object)

    async def success(self):
        responce: Responce
        responce = self._attempt_object.get_responce()
        if not await self.errors():
            return "unlocked" in responce.get_message()

class TestCheckCommon(TestAttemptSetUp):
    def setUp(self):
        super().setUp()
        self.create_check_objects()
        self.check_start_request()


    def create_check_objects(self):
        # Initialises Check objects
        # Its better to use class like CheckSample
        self.check = CheckSample(self.attempt)
        self.check2 = CheckSample(self.attempt2)
        self.check3 = CheckSample(self.attempt3)

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
        self.assertTrue(self.check.success())
        self.assertFalse(self.check2.success())

    def test_failure(self):
        self.assertFalse(self.check.failure())
        self.assertTrue(self.check2.failure())

        
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
    def setUp(self):
        super().setUp()
        self.create_check_objects()
        asyncio.run(self.check_start_request())

    def create_check_objects(self):
        # Initialises Check objects
        self.check = CheckSampleAsync(self.attempt)
        self.check2 = CheckSampleAsync(self.attempt2)
        self.check3 = CheckSampleAsync(self.attempt3)

        # Create new attempt objects to avoid changing ones used by
        # TestAttemptSetUpAsync.
        # This class may be reused by tests for AttackAsync class.
        self.create_attempt_objects()

    async def check_start_request(self):
        # Calls .start_request() of Attack objects
        # self.attack.start_request() would cause problems
        # if this class is inherited.
        attempt_obj = self.check.get_attempt_object()
        await attempt_obj.start_request()

        attempt_obj = self.check2.get_attempt_object()
        await attempt_obj.start_request()

        attempt_obj = self.check3.get_attempt_object()
        attempt_obj.request_should_fail = True
        await attempt_obj.start_request()

    def test_get_attempt_object(self):
        self.assertIsInstance(self.check.get_attempt_object(), AttemptAsync)

    async def test_success(self):
        self.assertTrue(await self.check.success())
        self.assertFalse(await self.check2.success())

    async def test_failure(self):
        self.assertFalse(await self.check.failure())
        self.assertTrue(await self.check2.failure())
        
    async def test_target_errors(self):
        self.assertEqual(await self.check.target_errors(), None)

    async def test_client_errors(self):
        self.assertFalse(await self.check.client_errors())
        self.assertTrue(await self.check3.client_errors())

    async def test_errors(self):
        self.assertFalse(await self.check.errors())
        self.assertTrue(await self.check3.errors())

    async def test_responce_errors(self):
        self.assertFalse(await self.check.responce_errors())
        self.assertFalse(await self.check3.responce_errors())



class TestCheck(TestCheckCommon, unittest.TestCase):
    pass


class TestCheckAsync(TestCheckAsyncCommon, unittest.IsolatedAsyncioTestCase):
    pass