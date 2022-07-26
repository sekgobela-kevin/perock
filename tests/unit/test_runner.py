import unittest

from perock.bforce import *
from perock.runner import *

from .test_bforce import SampleAttack
from .test_bforce import SampleAttackAsync
from .test_bforce import TestBForceBaseSetUP


class TestRunnerBaseSetUp(TestBForceBaseSetUP):    
    bforce_class = BForceBase
    attack_class = SampleAttack
    runner_class = RunnerBase

    def setUp(self):
        super().setUp()
        self.runner: Runner

    def create_attempt_objects(self):
        # Attempt objects are not needed here
        pass

    def create_bforce_objects(self):
        self.create_runner_objects()

    def create_runner_objects(self):
        self.runner = self.runner_class(self.attack_class)
        self.runner.set_target(self._target)
        self.runner.set_table(self.table)



class TestRunnerAsyncSetUp(TestRunnerBaseSetUp):
    bforce_class = BForceAsync
    attack_class = SampleAttackAsync
    runner_class = RunnerAsync

class TestRunnerBlockSetUp(TestRunnerBaseSetUp):
    bforce_class = BForceBlock
    attack_class = SampleAttack
    runner_class = RunnerBlock




class TestRunnerBaseCommon(TestRunnerBaseSetUp):
    # This class does not test the methods but just calls them.
    # Its just a check if the methods raises error.
    def test_set_target(self):
        self.runner.set_target(self._target)
    
    def test_set_table(self):
        self.runner.set_target(self._target)

    def test_enable_optimise(self):
        self.runner.enable_optimise()

    def test_enable_cancel_immediately(self):
        self.runner.enable_cancel_immediately()

    def test_disable_cancel_immediately(self):
        self.runner.disable_cancel_immediately()

    def test_set_max_success_records(self):
        self.runner.set_max_success_records(10)

    def test_disable_optimise(self):
        self.runner.disable_optimise()

    def test_get_success_records(self):
        self.runner.get_success_records()

    def test_get_cracked_records(self):
        self.runner.get_cracked_records()

    def test_set_max_parallel_primary_tasks(self):
        self.runner.set_max_parallel_primary_tasks(10)

    def test_create_bforce_object(self):
        pass

    def test_start(self):
        self.runner.start()

    def test_run(self):
        self.runner.run()


class TestRunnerParallel(TestRunnerBaseCommon):
    def test_set_max_parallel_tasks(self):
        self.runner.set_max_parallel_tasks(100)

    def test_set_max_workers(self):
        self.runner.set_max_workers(10)


class TestRunnerExecutorCommon(TestRunnerBaseCommon):
    def test_set_executor(self):
        self.runner.set_executor(self.thread_executor)


class TestRunnerThreadCommon(TestRunnerExecutorCommon):
    bforce_class = BForceThread
    attack_class = SampleAttack
    runner_class = RunnerThread


class TestRunnerBlockCommon(TestRunnerBlockSetUp, TestRunnerBaseCommon):
    pass


class TestRunnerAsyncCommon(TestRunnerAsyncSetUp, TestRunnerBaseCommon):
    async def test_start(self):
        await self.runner.start()

    async def test_run(self):
        await self.runner.run()



class TestRunnerThread(TestRunnerThreadCommon, unittest.TestCase):
    pass

class TestRunner(TestRunnerThreadCommon, unittest.TestCase):
    pass

class TestRunnerBlock(TestRunnerBlockCommon, unittest.TestCase):
    pass

class TestRunnerAsync(
    TestRunnerAsyncCommon, 
    unittest.IsolatedAsyncioTestCase):
    pass
