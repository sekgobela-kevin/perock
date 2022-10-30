import unittest
import aiounittest

from .test_attempt import TestAttemptCommon
from .test_attempt import TestAttemptAsyncCommon

from .test_check import TestCheckCommon
from .test_check import TestCheckAsyncCommon

from perock.target import Responce, Target
from perock.target import Account
from perock.attack import Attack, AttackAsync


class SampleAttack(Attack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self._target: Target
        self._responce: Responce
        self.request_should_fail = False
    
    def request(self):
        if not self.request_should_fail:
            account = Account(self._data)
            return self._target.login(account)
        else:
            return Exception()

    def success(self):
        if self.target_reached():
            if not self.errors():
                return "unlocked" in self._responce.get_message()
        return False

    def failure(self):
        if self.target_reached():
            if not self.errors():
                return "Failed to log" in self._responce.get_message()
        return False

    def set_responce(self, responce):
        self._responce = responce

    @classmethod
    def close_session(cls, session):
        session.close()

    @classmethod
    def close_responce(cls, session):
        session.close()


class SampleAttackAsync(AttackAsync):
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

    async def success(self):
        if await self.target_reached() and not await self.errors():
            return "unlocked" in self._responce.get_message()
        return False

    async def failure(self):
        if await self.target_reached():
            if not await self.errors():
                return "Failed to log" in self._responce.get_message()
        return False

    def set_responce(self, responce):
        self._responce = responce

    @classmethod
    async def close_session(cls, session):
        session.close()

    @classmethod
    async def close_responce(cls, session):
        session.close()


class CommonMethods():
    attack_class = SampleAttack

    def create_attempt_objects(self):
        # Initialise attempt objects
        # Attack object is also attempt object(inheritance)
        self.attempt = self.attack_class(self._target, self._data)
        self.attempt2 = self.attack_class(self._target, self.data2)
        self.attempt3 = self.attack_class(self._target, self.data3)


    def create_check_objects(self):
        # Initialise Check objects
        # Attack object is also Check object(inheritance)
        self.check = self.attack_class(self._target, self._data)
        self.check2 = self.attack_class(self._target, self.data2)
        self.check3 = self.attack_class(self._target, self.data3)


    def create_attack_objects(self):
        # Initialises attack objects
        self.attack = self.attack_class(self._target, self._data)
        self.attack2 = self.attack_class(self._target, self.data2)
        self.attack3 = self.attack_class(self._target, self.data3)


class TestAttackCommon(
    CommonMethods,TestAttemptCommon, TestCheckCommon):
    attack_class = SampleAttack

    def setUp(self):
        TestAttemptCommon.setUp(self)
        TestCheckCommon.setUp(self)
        self.create_attack_objects()

    def test_get_attempt_object(self):
        # get_attempt_object() should return self
        # The method is not needed within Attack class
        self.assertEqual(self.attack.get_attempt_object(), self.attack)

    def test_set_retries(self):
        self.attempt.set_retries(2)

    def test_set_retries_sleep_time(self):
        self.attempt.set_retries_sleep_time(2)

    def test_after_request(self):
        self.attack.after_request()

    def test_is_confused(self):
        self.attack.is_confused()

    def test_confused_action(self):
        with self.assertRaises(Exception):
            self.attack.confused_action()

    def start_until_target_reached(self):
        self.attack.until_target_reached()

    def test_start_until_retries(self):
        self.attack.start_until_retries()


class TestAttackAsyncCommon(
    CommonMethods, TestAttemptAsyncCommon, TestCheckAsyncCommon):
    attack_class = SampleAttackAsync

    def setUp(self):
        TestAttemptAsyncCommon.setUp(self)
        TestCheckAsyncCommon.setUp(self)
        self.create_attack_objects()

    async def test_after_request(self):
        await self.attack.after_request()

    async def test_confused_action(self):
        with self.assertRaises(Exception):
            await self.attack.confused_action()

    async def start_until_target_reached(self):
        await self.attack.until_target_reached()

    async def test_start_until_retries(self):
        await self.attack.start_until_retries()




class TestAttack(TestAttackCommon, unittest.TestCase):
    pass

class TestAttackAsync(TestAttackAsyncCommon, aiounittest.AsyncTestCase):
    pass
