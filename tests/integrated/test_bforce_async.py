import unittest
import asyncio

from perock.bforce import BForceAsync

from common_classes import AttackAsyncSample
from test_bforce import BForceCommonTest


class BForceAsyncCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = BForceAsync(self.target, self.table)
        self.bforce.set_attack_class(AttackAsyncSample)

    def start(self):
        asyncio.run(self.bforce.start())


class BForceAsyncTest(BForceAsyncCommonTest, unittest.TestCase):
    pass
