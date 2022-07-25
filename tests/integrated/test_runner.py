import unittest
import asyncio
#import timeout_decorator

import test_bforce
import common_classes

from perock import runner

# Tests for this test module are based non IO blocking activity.
# It involves bruteforce with passwords and usernames from file system.
# Product of usernames and passwords is calculated.
# Each username-password combination is campared with other defined 
# username-password.

# There is no waiting, so there is no IO blocking activity taking place.
# RunnerAsync and Runner are expected to perform slower than RunnerBlock.
# RunnerAsync and Runner were designed for IO blocking activity and 
# they will perform worst on CPU intensive activities.

# Setting ProccessPoolExecutor is failing as seen in the tests.
# RunnerAsync and Runner will peform better on IO bound tasks such
# as performing internet request.


class RunnerSetUp(test_bforce.BForceSetUp):
    def setup_bforce_object(self):
        self.setup_runner()

    def setup_runner(self):
        self.runner = runner.Runner(common_classes.AttackSample)
        self.runner.set_target(self._target)
        self.runner.set_table(self.table)
    
    def start(self):
        # Calls .run() of runner object
        self.runner.run()

class RunnerBlockSetUp(test_bforce.BForceSetUp):
    def setup_runner(self):
        self.runner = runner.RunnerBlock(common_classes.AttackSample)
        self.runner.set_target(self._target)
        self.runner.set_table(self.table)

class RunnerAsyncSetUp(test_bforce.BForceSetUp):
    def setup_runner(self):
        self.runner = runner.RunnerAsync(common_classes.AttackAsyncSample)
        self.runner.set_target(self._target)
        self.runner.set_table(self.table)


class RunnerCommonTest(RunnerSetUp):
    #@timeout_decorator.timeout(12)
    def test_start_not_optimised(self):
        self.runner.disable_optimise()
        self.start()
        self.assertCountEqual(self.runner.get_success_records(), self.accounts)

    #@timeout_decorator.timeout(10)
    def test_start_optimised(self):
        self.runner.enable_optimise()
        self.start()
        self.assertCountEqual(self.runner.get_success_records(), self.accounts)

    #@timeout_decorator.timeout(5)
    def test_start_cancel_immediately(self):
        self.runner.enable_cancel_immediately()
        self.start()
        self.assertEqual(len(self.runner.get_success_records()), 1)

    #@timeout_decorator.timeout(5)
    def test_set_max_success_records(self):
        self.runner.set_max_success_records(1)
        self.start()
        self.assertEqual(len(self.runner.get_success_records()), 1)


    #@timeout_decorator.timeout(5)
    def test_set_executor(self):
        # Proccess executor wont work on threaded environment
        self.runner.set_executor(self.process_executor)
        with self.assertRaises(TypeError):
            # cannot pickle '_thread._local' object
            self.start()

        self.runner.enable_cancel_immediately()
        self.runner.set_executor(self.thread_executor)
        self.start()
        self.assertEqual(len(self.runner.get_success_records()), 1)
        

    #@timeout_decorator.timeout(5)
    def test_other_methods(self):
        self.runner.enable_cancel_immediately()
        self.runner.set_max_parallel_primary_tasks(10)
        self.runner.set_max_workers(15)
        self.runner.set_max_parallel_tasks(100)
        self.start()
        self.assertEqual(len(self.runner.get_success_records()), 1)


class RunnerBlockCommonTest(RunnerBlockSetUp, RunnerCommonTest):
    def setUp(self):
        super().setUp()
        RunnerCommonTest.setUp(self)

    def test_set_executor(self):
        # RunnerBlock does not use executor
        pass

class RunnerAsyncCommonTest(RunnerAsyncSetUp, RunnerCommonTest):
    def setUp(self):
        super().setUp()
        RunnerCommonTest.setUp(self)

    def start(self):
        asyncio.run(self.runner.run())

    def test_set_executor(self):
        # RunnerAsync does not use executor
        pass


class RunnerTest(RunnerCommonTest, unittest.TestCase):
   pass

class RunnerBlockTest(RunnerBlockCommonTest, unittest.TestCase):
   pass

class RunnerBlockTest(RunnerAsyncCommonTest, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
