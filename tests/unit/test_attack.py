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
            return self.fail_responce

    def set_responce(self, responce):
        self.responce = responce


class TestAttackMixin():
    def __init(*args, **kwargs):
        pass


class TestAttackCommon(TestAttemptCommon, TestCheckCommon):
    def setUp(self):
        super().setUp()
        super(TestCheckCommon, self).setUp()

        # Initialise attack objects
        self.attack = SampleAttack(self.target, self.data)
        self.attack2 = SampleAttack(self.target, self.data2)
        self.attack3 = SampleAttack(self.target, self.data3)

        # Sets sleep sleep time to zero
        #self.attack.set_sleep_time(0)
        #self.attack2.set_sleep_time(0)
        #self.attack3.set_sleep_time(0)

        # Initialise attempt objects
        # Attack object is also attempt object(inheritance)
        self.attempt = SampleAttack(self.target, self.data)
        self.attempt2 = SampleAttack(self.target, self.data2)
        self.attempt3 = SampleAttack(self.target, self.data3)

        # Initialises Check objects
        # Attack object is also Check object(inheritance)
        self.check = SampleAttack(self.target, self.data)
        self.check2 = SampleAttack(self.target, self.data2)
        self.check3 = SampleAttack(self.target, self.data3)

        # TestCheckCommon requires start_request() to be called
        self.check.start_request()
        self.check2.start_request()
        self.check3.start_request()

    def test_get_attempt_object(self):
        # get_attempt_object() should return self
        # The method is not needed within Attack class
        self.assertEqual(self.attack.get_attempt_object(), self.attack)


class TestAttempt(TestAttackCommon, unittest.TestCase):
    pass


