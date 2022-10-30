import asyncio
import unittest
import concurrent
import aiounittest


from perock import bforce
from perock import runner
from perock import attack
from perock import forcetable



class SetUp():
    # Defines passwprds and usernames
    _usernames = ["Ben", "Jackson", "Marry"]
    _passwords = range(5)

    # Success records
    _success_records = [
        {"username": "Ben", "password": 0},
        {"username": "Marry", "password": 1},
        {"username": "Marry", "password": 4},
        {"username": "Jackson", "password": 3}
    ]


class SampleAttack(attack.Attack):
    def request(self):
        return self._data

    def success(self):
        return self._data in SetUp._success_records

    def failure(self):
        return self._data not in SetUp._success_records

    def target_reached(self):
        return True

    def client_error(self):
        return False

    def target_error(self):
        return False

class SampleAttackAsync(attack.AttackAsync):
    async def request(self):
        return self._data

    async def success(self):
        return self._data in SetUp._success_records

    async def failure(self):
        return self._data not in SetUp._success_records

    async def target_error(self):
        return False


class TestRunnerBaseSetUp(SetUp):    
    _bforce_type = bforce.BForceBase
    _attack_type = SampleAttack
    _runner_type = runner.RunnerBase

    @classmethod
    def setUpClass(cls) -> None:

        # Defines field to use with table to create records.
        cls._usernames_field = forcetable.Field("username", cls._usernames)
        cls._passwords_field = forcetable.Field("password", cls._passwords)

        # Table contains cartesian product of fields as records.
        cls._table = forcetable.Table()
        cls._table.add_primary_field(cls._usernames_field)
        cls._table.add_field(cls._passwords_field)

        cls._target = "fake target"


    def setUp(self):
        self._runner = self._runner_type(
            self._attack_type, 
            target=self._target,
            table=self._table,
            optimise=False,
        )

    def start_runner(self):
        if isinstance(self._runner, runner.RunnerAsync):
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._runner.start())
            loop.close()
        else:
            self._runner.start()



class TestRunnerAsyncSetUp(TestRunnerBaseSetUp):
    _bforce_type = bforce.BForceAsync
    _attack_type = SampleAttackAsync
    _runner_type = runner.RunnerAsync


class TestRunnerBlockSetUp(TestRunnerBaseSetUp):
    _bforce_type = bforce.BForceBlock
    _attack_type = SampleAttack
    _runner_type = runner.RunnerBlock




class TestRunnerBaseCommon(TestRunnerBaseSetUp):
    # This class does not test the methods but just calls them.
    # Its just a check if the methods raises error.

    def test_enable_optimise(self):
        self._runner.enable_optimise()

    def test_enable_cancel_immediately(self):
        self._runner.enable_cancel_immediately()

    def test_disable_cancel_immediately(self):
        self._runner.disable_cancel_immediately()

    def test_set_max_success_records(self):
        self._runner.set_max_success_records(10)

    def test_disable_optimise(self):
        self._runner.disable_optimise()

    def test_get_success_records(self):
        self._runner.get_success_records()

    def test_get_cracked_records(self):
        self._runner.get_cracked_records()

    def test_set_max_multiple_primary_items(self):
        self._runner.set_max_multiple_primary_items(10)

    def test_test_get_table(self):
        self.assertEqual(self._runner.get_table(), self._table)

    def test_is_primary_optimised(self):
        self.assertEqual(self._runner.is_primary_optimised(), False)

    def test_session_exists(self):
        self.assertFalse(self._runner.session_exists())

    def test_set_session(self):
        self._runner.set_session(object())
        self.assertTrue(self._runner.session_exists())

    def test_get_session(self):
        session = object()
        self._runner.set_session(session)
        self.assertEqual(self._runner.get_session(), session)

    def test_get_success_records(self):
        self.assertEqual(self._runner.get_success_records(), [])
        self.start_runner()
        self.assertCountEqual(self._runner.get_success_records(), 
            self._success_records)

    # def test_success_exists(self):
    #     self.assertFalse(self._runner.success_exists())
    #     self.start_runner()
    #     self.assertTrue(self._runner.success_exists())


    def test_get_runner_time(self):
        self.assertEqual(self._runner.get_runner_time(), 0)
        self.start_runner()
        self.assertGreaterEqual(self._runner.get_runner_time(), 0)

    def test_is_running(self):
        self.assertFalse(self._runner.is_running())
        self.start_runner()
        self.assertFalse(self._runner.is_running())

    def test_started(self):
        self.assertFalse(self._runner.started())
        self.start_runner()
        self.assertTrue(self._runner.started())

    def test_completed(self):
        self.assertFalse(self._runner.completed())
        self.start_runner()
        self.assertTrue(self._runner.started())

    def test_stop(self):
        self.start_runner()
        self._runner.stop()

    def test_run(self):
        self._runner.run()

    def test_start(self):
        self.start_runner()


class TestRunnerParallel(TestRunnerBaseCommon):
    def test_set_max_parallel_tasks(self):
        self._runner.set_max_parallel_tasks(100)

    def test_set_max_workers(self):
        self._runner.set_max_workers(10)


class TestRunnerExecutorCommon(TestRunnerBaseCommon):
    def test_set_executor(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self._runner.set_executor(executor)


class TestRunnerThreadCommon(TestRunnerExecutorCommon):
    _bforce_type = bforce.BForceThread
    _attack_type = SampleAttack
    _runner_type = runner.RunnerThread


class TestRunnerBlockCommon(TestRunnerBlockSetUp, TestRunnerBaseCommon):
    pass


class TestRunnerAsyncCommon(TestRunnerAsyncSetUp, TestRunnerBaseCommon):
    async def test_start(self):
        await self._runner.start()

    async def test_run(self):
        await self._runner.run()



class TestRunnerThread(TestRunnerThreadCommon, unittest.TestCase):
    pass

class TestRunner(TestRunnerThreadCommon, unittest.TestCase):
    pass

class TestRunnerBlock(TestRunnerBlockCommon, unittest.TestCase):
    pass

class TestRunnerAsync(TestRunnerAsyncCommon, aiounittest.AsyncTestCase):
    pass
