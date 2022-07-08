import unittest
import asyncio

from perock.bforce import BForceBlock

from common_classes import AttackSample
from test_bforce import BForceCommonTest


class BForceBockCommonTest(BForceCommonTest):
    def setup_bforce_object(self):
        self.bforce = BForceBlock(self.target, self.ftable)
        self.bforce.set_attack_class(AttackSample)



class BForceBlockTest(BForceCommonTest, unittest.TestCase):
    pass
