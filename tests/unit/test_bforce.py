import asyncio
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Executor
from concurrent.futures import Future
from typing import Type
import unittest

import aiounittest


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
from perock.bforce import BForceBlock


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


class TestBForceBaseSetUP(TestTableSetUp, TestAttemptSetUp):
    bforce_class: Type[BForce]
    attack_class: Type[SampleAttack]

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


class TestBForceBaseCommon(TestBForceBaseSetUP):
    def test_enable_cancel_immediately(self):
        self.bforce.enable_cancel_immediately()

    def test_disable_cancel_immediately(self):
        self.bforce.disable_cancel_immediately()

    def test_set_max_success_records(self):
        self.bforce.set_max_success_records(10)


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

    def session_exists(self):
        self.bforce.set_session(self._session)
        self.assertTrue(self.bforce.session_exists())
        self.assertFalse(self.bforce_raw.session_exists())

    def test_get_session(self):
        self.assertEqual(self.bforce_raw.get_session(), None)
        self.bforce.set_session(self._session)
        self.assertIsInstance(self.bforce.get_session(), Session)
        # Same session be returned
        session = self.bforce.get_session()
        self.assertEqual(self.bforce.get_session(), session)

    def test_get_create_session(self):
        # This test method is similar to test_get_session()
        #self.assertEqual(self.bforce_raw.get_create_session(), None)
        self.bforce.set_session(self._session)
        # Same session be returned
        session = self.bforce.get_session()
        self.assertEqual(self.bforce.get_create_session(), session)


    def test_set_attack_class(self):
        self.bforce_raw.set_attack_class(self.attack_class)
        self.assertEqual(self.bforce_raw.get_attack_class(), self.attack_class)

    def test_get_attack_class(self):
        self.assertEqual(self.bforce.get_attack_class(), self.attack_class)

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


    def test_start(self):
        # This is not a test but call to method
        self.bforce.start()



class TestBForceParallelCommon(TestBForceBaseCommon):
    def test_set_max_workers(self):
        self.bforce.set_max_workers(2)

    def test_set_max_parallel_tasks(self):
        # Hard to test
        self.bforce.set_max_parallel_tasks(10)

    def test_to_future(self):
        raise NotImplementedError

    def test_handle_attack_recursive_future(self):
        raise NotImplementedError

    def test_wait_tasks(self):
        raise NotImplementedError


class TestBForceExecutorCommon(TestBForceParallelCommon):
    def test_set_executor(self):
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.get_executor(), self.process_executor)

    def test_get_executor(self):
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.get_executor(), self.process_executor)


    def test_create_default_executor(self):
        executor = self.bforce.create_default_executor()
        self.assertIsInstance(executor, Executor)

    def test_create_get_executor(self):
        self.assertIsInstance(self.bforce.create_get_executor(), 
        ThreadPoolExecutor)
        self.bforce.set_executor(self.process_executor)
        self.assertEqual(self.bforce.create_get_executor(), 
        self.process_executor)

    def test_to_future(self):
        with self.bforce.create_default_executor() as executor:
            self.bforce.set_executor(executor)
            future = self.bforce.to_future(lambda : None)
            self.assertIsInstance(future, Future)

    def test_handle_attack_recursive_future(self):
        with self.bforce.create_default_executor() as executor:
            self.bforce.set_executor(executor)
            future = self.bforce.handle_attack_recursive_future(
                self.common_record)
            self.assertIsInstance(future, Future)

    def test_wait_tasks(self):
        with self.bforce.create_default_executor() as executor:
            self.bforce.set_executor(executor)
            future1 = self.bforce.to_future(lambda : None)
            future2 = self.bforce.to_future(lambda : None)
            self.bforce.wait_tasks([future1, future2])


class TestBForceThreadCommon(TestBForceExecutorCommon):
    bforce_class = BForce
    attack_class = SampleAttack


class TestBForceBlockCommon(TestBForceBaseCommon):
    bforce_class = BForceBlock
    attack_class = SampleAttack


class TestBForceAsyncCommon(TestBForceParallelCommon):
    bforce_class: Type[BForceAsync] = BForceAsync
    attack_class: Type[SampleAttackAsync] = SampleAttackAsync

    async def test_create_session(self):
        with self.assertRaises(AttributeError):
            # No attack class
            await self.bforce_raw.create_session()
        #self.assertEqual(self.bforce_raw.create_session(), None)
        self.assertIsInstance(await self.bforce.create_session(), Session)

    async def test_get_create_session(self):
        # This test method is similar to test_get_session()
        #self.assertEqual(await self.bforce_raw.get_create_session(), None)
        self.bforce.set_session(self._session)
        # Same session be returned
        session = self.bforce.get_session()
        self.assertEqual(await self.bforce.get_create_session(), session)

    async def test_close_session(self):
        self.bforce.set_session(self._session)
        await self.bforce.close_session()
        session = self.bforce.get_session()
        self.assertTrue(session.closed)


    async def test_to_future(self):
        async def async_func():
            pass
        future = self.bforce.to_future(async_func)
        self.assertIsInstance(future, asyncio.Task)

    async def test_handle_attack_recursive_future(self):
        future = self.bforce.handle_attack_recursive_future(
            self.common_record)
        self.assertIsInstance(future, asyncio.Task)

    async def test_wait_tasks(self):
        async def async_func():
            pass
        future1 = self.bforce.to_future(async_func)
        future2 = self.bforce.to_future(async_func)
        await self.bforce.wait_tasks([future1, future2])
        # Theres no way to assert the method
        # Its better to just test if exceptions get raised


    async def test_start(self):
        # This is not a test but call to method
        await self.bforce.start()




class TestBForceBlock(TestBForceBlockCommon, unittest.TestCase):
    pass

class TestBForceAsync(TestBForceAsyncCommon, aiounittest.AsyncTestCase):
    pass

class TestBForce(TestBForceThreadCommon, unittest.TestCase):
    pass
