import unittest

from common_classes import *
from common_test import *

from perock import target


class PerockTestTarget(target.Target):
    def __init__(self, accounts: Iterable[Account] = ...) -> None:
        super().__init__(accounts)
        self.set_responce_time(1)


class PerockTest(CommonTest, unittest.TestCase):
    def test_ss(self):
        pass
     