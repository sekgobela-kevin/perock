import unittest

from .test_attempt import TestAttemptCommon
from .test_check import TestCheckCommon

from perock.target import Target
from perock.target import Account
from perock.attack import Attack


class SampleAttack(Attack):
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


class TestAttackMixin():
    def __init(*args, **kwargs):
        pass


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


class TestAttempt(TestAttackCommon, unittest.TestCase):
    pass


