from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Executor
import queue
import unittest


from perock.attempt import Attempt
from perock.target import Target
from perock.target import Account

from .common_classes import Session
from .common_classes import Responce

from .test_forcetable import TestTableSetUp
from .test_attempt import TestAttemptSetUp
from .test_attempt import TestAttemptSetUpAsync
from .test_attack import SampleAttack
from .test_attack import SampleAttackAsync

from perock.attack import Attack
from perock.attack import AttackAsync

from perock.bforce import BForce
from perock.bforce import BForceAsync


class SampleAttack(SampleAttack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)

    def create_session():
        return Session()


class SampleAttackAsync(SampleAttackAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)

    async def create_session():
        return Session()


class TestBForceSetUP(TestTableSetUp, TestAttemptSetUp):
    bforce_class = BForce
    attack_class = SampleAttack

    @classmethod
    def setUpClass(cls):
        cls.process_executor = ProcessPoolExecutor()
        cls.thread_executor = ThreadPoolExecutor()

    def setUp(self):
        super().setUp()
        # Does not matter which AttempSetUP class used
        TestAttemptSetUp.setUp(self)
        self.create_bforce_objects()

    def create_bforce_objects(self):
        self.bforce = self.bforce_class(self._target, self.table)
        self.bforce.set_attack_class(self.attack_class)
        # Has no attack class
        self.bforce_raw = self.bforce_class(self._target, self.table)


class TestBForceCommon(TestBForceSetUP):
    def test_enable_cancel_immediately(self):
        self.bforce.enable_cancel_immediately()

    def test_disable_cancel_immediately(self):
        self.bforce.disable_cancel_immediately()

    def test_set_max_success_records(self):
        self.bforce.set_max_success_records(10)

    def test_set_executor(self):
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.get_executor(), self.process_executor)


    def test_get_executor(self):
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.get_executor(), self.process_executor)

    def test_set_max_workers(self):
        self.bforce.set_max_workers(2)

    def test_create_or_get_executor(self):
        self.assertIsInstance(self.bforce.create_or_get_executor(), 
        ThreadPoolExecutor)
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.create_or_get_executor(), 
        self.process_executor)

    def test_set_max_parallel_tasks(self):
        # Hard to test
        self.bforce.set_max_parallel_tasks(10)


    def test_create_session(self):
        with self.assertRaises(AttributeError):
            # No attack class
            self.bforce_raw.create_session()
        #self.assertEqual(self.bforce_raw.create_session(), None)
        self.assertIsInstance(self.bforce.create_session(), Session)

    def test_close_session(self):
        self.bforce.set_session(self._session)
        self.bforce.close_session()
        self.assertTrue(self.bforce.get_session().closed)


    def test_get_session(self):
        with self.assertRaises(AttributeError):
            # Theres no attack class in bforce_raw
            # Its better to set session manually
            self.bforce_raw.get_session()
        #self.assertEqual(self.bforce_raw.get_session(), None)
        self.assertIsInstance(self.bforce.get_session(), Session)
        # Same session be returned
        session = self.bforce.get_session()
        self.assertEqual(self.bforce.get_session(), session)

    def test_set_attack_class(self):
        self.bforce_raw.set_attack_class(self.attack_class)
        self.assertEqual(self.bforce_raw.get_attack_class(), self.attack_class)

    def test_get_attack_class(self):
        self.assertEqual(self.bforce.get_attack_class(), self.attack_class)

    def test_attack_class_async(self):
        self.assertFalse(self.bforce.attack_class_async())

    def test_create_attack_object(self):
        attack_object = self.bforce.create_attack_object(self._data)
        self.assertIsInstance(attack_object, self.attack_class)
        with self.assertRaises(AttributeError):
            # bforce_raw does not hae attack class
            self.bforce_raw.create_attack_object(self._data)

    def test_get_current_producer_method(self):
        self.assertTrue(callable(self.bforce.get_current_producer_method()))

    def test_get_producer_records(self):
        self.bforce.get_current_producer_method()()

    def test_set_max_parallel_primary_tasks(self):
        self.bforce.set_max_parallel_primary_tasks(10)


    def test_clear_queue(self):
        queue_object = queue.Queue(10)
        for i in range(10):
            queue_object.put(i)
        self.bforce.clear_queue(queue_object)
        self.assertTrue(queue_object.empty())


    def test_start(self):
        # This is not a test but call to method
        self.bforce.start()



class TestBForceAsyncCommon(TestBForceCommon):
    bforce_class = BForceAsync
    attack_class = SampleAttackAsync

    def test_set_attack_class(self):
        self.bforce_raw.set_attack_class(self.attack_class)
        self.assertEqual(self.bforce_raw.get_attack_class(), self.attack_class)

    def test_get_attack_class(self):
        self.assertEqual(self.bforce.get_attack_class(), self.attack_class)

    def test_attack_class_async(self):
        self.assertTrue(self.bforce.attack_class_async())

    def test_create_attack_object(self):
        attack_object = self.bforce.create_attack_object(self._data)
        self.assertIsInstance(attack_object, self.attack_class)
        with self.assertRaises(AttributeError):
            # bforce_raw does not hae attack class
            self.bforce_raw.create_attack_object(self._data)

    async def test_create_session(self):
        with self.assertRaises(AttributeError):
            # No attack class
            await self.bforce_raw.create_session()
        #self.assertEqual(self.bforce_raw.create_session(), None)
        self.assertIsInstance(await self.bforce.create_session(), Session)

    async def test_close_session(self):
        self.bforce.set_session(self._session)
        await self.bforce.close_session()
        session = await self.bforce.get_session()
        self.assertTrue(session.closed)


    async def test_get_session(self):
        with self.assertRaises(AttributeError):
            # Theres no attack class in bforce_raw
            # Its better to set session manually
            await self.bforce_raw.get_session()
        #self.assertEqual(self.bforce_raw.get_session(), None)
        self.assertIsInstance(await self.bforce.get_session(), Session)
        # Same session be returned
        session = await self.bforce.get_session()
        self.assertEqual(await self.bforce.get_session(), session)

    async def test_start(self):
        # This is not a test but call to method
        await self.bforce.start()


class TestBForce(TestBForceCommon, unittest.TestCase):
    pass

class TestBForceAsync(TestBForceAsyncCommon, unittest.IsolatedAsyncioTestCase):
    pass
