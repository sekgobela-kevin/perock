import unittest

from .test_attempt import TestAttemptCommon
from .test_attempt import TestAttemptAsyncCommon

from .test_check import TestCheckCommon
from .test_check import TestCheckAsyncCommon

from perock.target import Responce, Target
from perock.target import Account
from perock.attack import Attack, AttackAsync, AttackText, AttackTextAsync


class SampleAttack(Attack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.target: Target
        self.responce: Responce
        self.request_should_fail = False
    
    def request(self):
        if not self.request_should_fail:
            account = Account(self.data)
            return self.target.login(account)
        else:
            return Exception()

    def success(self):
        if not self.errors():
            return "unlocked" in self.responce.get_message()

    def set_responce(self, responce):
        self.responce = responce


class SampleAttackText(AttackText):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.target: Target
        self.responce: Responce
        self.request_should_fail = False

        self.set_success_bytes_strings(["unlocked"])
        self.set_failure_bytes_strings(["Failed to log"])
        self.set_target_error_bytes_strings(["Our system"])

    def responce_content(self) -> str:
        if self.target_reached():
            return self.responce.get_message()
        else:
            return str(self.responce)
    
    def request(self):
        if not self.request_should_fail:
            account = Account(self.data)
            return self.target.login(account)
        else:
            return Exception()

    def set_responce(self, responce):
        self.responce = responce


class SampleAttackAsync(AttackAsync):
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

    async def success(self):
        if not await self.errors():
            return "unlocked" in self.responce.get_message()

    def set_responce(self, responce):
        self.responce = responce


class SampleAttackTextAsync(AttackTextAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.target: Target
        self.responce: Responce
        self.request_should_fail = False

        self.set_success_bytes_strings(["unlocked"])
        self.set_failure_bytes_strings(["Failed to log"])
        self.set_target_error_bytes_strings(["Our system"])

    async def responce_content(self) -> str:
        if self.target_reached():
            return self.responce.get_message()
        else:
            return str(self.responce)
    
    async def request(self):
        if not self.request_should_fail:
            account = Account(self.data)
            return self.target.login(account)
        else:
            return Exception()

    def set_responce(self, responce):
        self.responce = responce


class TestAttackCommon(TestAttemptCommon, TestCheckCommon):
    def setUp(self):
        super().setUp()
        super(TestCheckCommon, self).setUp()
        self.create_attack_objects()

    def create_attempt_objects(self):
        # Initialise attempt objects
        # Attack object is also attempt object(inheritance)
        self.attempt = SampleAttack(self.target, self.data)
        self.attempt2 = SampleAttack(self.target, self.data2)
        self.attempt3 = SampleAttack(self.target, self.data3)


    def create_check_objects(self):
        # Initialise Check objects
        # Attack object is also Check object(inheritance)
        self.check = SampleAttack(self.target, self.data)
        self.check2 = SampleAttack(self.target, self.data2)
        self.check3 = SampleAttack(self.target, self.data3)


    def create_attack_objects(self):
        # Initialises attack objects
        self.attack = SampleAttack(self.target, self.data)
        self.attack2 = SampleAttack(self.target, self.data2)
        self.attack3 = SampleAttack(self.target, self.data3)

    def check_start_request(self):
        # Calls .start_request() to Attempt object of Check object.
        # Remember that Attack is subclass of Check.
        # The objects are just Attack object in chech named variables.
        self.check.start_request()
        self.check2.start_request()
        self.check3.request_should_fail = True
        self.check3.start_request()

    def test_get_attempt_object(self):
        # get_attempt_object() should return self
        # The method is not needed within Attack class
        self.assertEqual(self.attack.get_attempt_object(), self.attack)


class TestAttackTextCommon(TestAttackCommon):
    def create_check_objects(self):
        # Initialise Check objects
        # Attack object is also Check object(inheritance)
        self.check = SampleAttackText(self.target, self.data)
        self.check2 = SampleAttackText(self.target, self.data2)
        self.check3 = SampleAttackText(self.target, self.data3)

    def test_target_errors(self):
        self.assertFalse(self.check.target_errors())


class TestAttackAsyncCommon(TestAttemptAsyncCommon, TestCheckAsyncCommon):
    pass


class TestAttackTextAsyncCommon(TestAttackAsyncCommon):
    def create_check_objects(self):
        # Initialises Check objects
        self.check = SampleAttackTextAsync(self.target, self.data)
        self.check2 = SampleAttackTextAsync(self.target, self.data2)
        self.check3 = SampleAttackTextAsync(self.target, self.data3)

        # Create new attempt objects to avoid changing ones used by
        # TestAttemptSetUpAsync.
        # This class may be reused by tests for AttackAsync class.
        self.create_attempt_objects()

    async def test_target_errors(self):
        self.assertFalse(await self.check.target_errors())





class TestAttack(TestAttackCommon, unittest.TestCase):
    pass

class TestAttackText(TestAttackTextCommon, unittest.TestCase):
    pass

class TestAttackAsync(TestAttackAsyncCommon, unittest.IsolatedAsyncioTestCase):
    pass

class TestAttackTextAsync(
    TestAttackTextAsyncCommon, 
    unittest.IsolatedAsyncioTestCase):
    pass


