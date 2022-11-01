'''
Performs attack with multiple attempts

Attempts will be performed conccurently with threads or asyncio
which should improve performance. Use of threads and asyncio should
make attack fast as each attempts are executed in concurrently.

Classes in this module only define how multiple attacks can be conducted
but not how it would be conducted. That could be perfomed with attack 
module which offers methods for defining how to interact with target
or system e.g webpage form.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''

# This module is getting complex as it grecords it grecords.
# It becomes pain to maintain this module as its classes are large.
# Its a pain to maintain module with lines closer to 1000
# It needs to be split into smaller modules or its classes split.

# Each class in the modue contain methods that could be split to other 
# classes.
# Methods involving session and producer can be made their own classes.
# Theres also a need for base class for BForce classes.
# Its also a pain to maintain async version of BForce class.

# This module has grecordn beyond what was planned.
# It was supposed to contain one class but now has 3 classes.
# Each class implements methods their own way which adds even more lines.


from typing import Callable, Dict, Iterable, List, Set, Type
import threading
import multiprocessing
import time

import asyncio
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import Future
from concurrent.futures import Executor
#from concurrent.futures import as_completed
#import concurrent.futures


from .attack import Attack
from .attack import AttackAsync

from .forcetable import Field
from .forcetable import Record
from .forcetable import Table

from . import forcetable

from . import producer
from . import exceptions


# Not used
#from .session import BForceSession
#from .session import BForceBlockSession
#from .session import BForceAsyncSession



class BForceBase():
    '''Base class for performing bruteforce on target with provided
    attack class and table object'''
    _base_attack_type = Attack

    def __init__(self, target, table:Table, optimise=False) -> None:
        self._target = target
        self._table = table
        self._optimise = optimise
        self._fields = table.get_fields()
        self._item_names = table.get_item_names()

        # Attack class/type to use with bforce
        self._attack_class = None

        # If True, pending tasks will be stopped on first success.
        # producer and _consumer will also be stopped.
        self._cancel_immediately = False
        # Maximum success records
        self._max_success_records = None
        # Maximum primary items with success(e.g 4 usernames success)
        self._max_success_primary_items = None

        # Changed callback when producer or _consumer completes
        self._producer_completed = False
        self._consumer_completed = False

        # If False, producer would stop
        self._producer_should_run = True
        self._consumer_should_run = True

        # Primary items of cracked records
        self._success_primary_items = set()
        # Contains success/cracked record
        self._success_records = []
        # Map containing primary items(keys) and success records(values)
        self._success_primary_items_map = {}


        # Primary items excluded from being bruteforced.
        self._excluded_primary_items = set()


        # This sets maximum parallel primary items tasks
        # e.g multiples usernames can be executed at same time.
        self._max_multiple_primary_items = 1
        # Maximum success records for primary item before switching.
        # If reached, primary item records will be switched.
        self._max_primary_success_records = 1

        # producer records
        self._producer_records = iter(self.producer())

        # Callabck callback functions to be called on state change.
        self._start_callback = lambda: None
        self._done_callback = lambda: None
        self._producer_switch_callback = None
        #self._after_attack_callback = lambda: None

        # # Producer related callback functions
        # self._producer_done_callback = lambda: None
        

        # # Attack class related callbackfunctions
        # self._target_reached_callback = None
        # self._target_errors_callback = None
        # self._client_errors_callback = None
        # self._errors_callback = None
        # self._success_callback = None
        # self._failure_callback = None

    # Start for setting callback functions
    def set_start_callback(self, callback):
        self._start_callback = callback

    def set_done_callback(self, callback):
        self._done_callback = callback 

    def set_producer_switch_callback(self, callback):
        self._producer_switch_callback = callback 

    # def set_after_attack_callback(self, callback):
    #     self._after_attack_callback = callback 

    def enable_optimise(self):
        self._optimise = True

    def disable_optimise(self):
        self._optimise = False

    def enable_cancel_immediately(self):
        self._cancel_immediately = True

    def disable_cancel_immediately(self):
        self._cancel_immediately = False

    def set_max_success_records(self, total):
        self._max_success_records = total

    def set_max_multiple_primary_items(self, total):
        self._max_multiple_primary_items = total

    def set_max_success_primary_items(self, total):
        self._max_success_primary_items = total

    def set_max_primary_success_records(self, total):
        self._max_primary_success_records = total

    def get_table(self):
        # Gets table with records to bruteforce.
        return self._table

    def get_excluded_primary_items(self):
        # Excluded primary items may contain success primary items.
        return self._excluded_primary_items

    def get_success_records(self):
        return self._success_records

    def get_success_primary_items(self):
        return self._success_primary_items

    def primary_item_successful(self, primary_item):
        # Checks if primary item has successful records
        return primary_item in self._success_primary_items_map

    def get_primary_success_records(self, primary_item):
        # Gets successful records for primary item
        if self.primary_item_successful(primary_item):
            return self._success_primary_items_map[primary_item]
        return []

    def add_excluded_primary_item(self, primary_item):
        # Adds primary item to excluded primary items.
         self._excluded_primary_items.add(primary_item)

    def add_excluded_primary_items(self, primary_items):
        # Adds primary items to excluded primary items.
        for item in primary_items:
            self.add_excluded_primary_item(item)

    def remove_excluded_primary_item(self, primary_item):
        # Removes primary item from excluded primary items.
        self._excluded_primary_items.discard(primary_item)

    def remove_excluded_primary_items(self, primary_items):
        # Removes primary items from excluded primary items.
        for item in primary_items:
            self.remove_excluded_primary_item(item)

    def should_optimise(self):
        # Checks if optimisations should be applied.
        return self._optimise and self._table.primary_field_exists()

    def is_primary_optimised(self):
        # Checks primary optimations are enabled.
        return self.should_optimise()

    def create_session(self, *args, **kwargs):
        # Creates session object to be shared with attack objects
        attack_class = self.get_attack_class()
        try:
            # Ask attack class to create session
            session = attack_class.create_session(*args, **kwargs)
        except NotImplementedError:
            # Return None if attack class cant create session
            return None
        else:
            # Return session created by attack class
            return session


    # Start: session methods

    def session_exists(self):
        # Returns True if session exists
        raise NotImplementedError

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        raise NotImplementedError

    def get_session(self):
        # Gets session object
        raise NotImplementedError

    def get_create_session(self):
        # Gets session object to be shared with attack objects
        # Realise the use of thread_local
        # self._local was created from threading.local()
        if not self.session_exists():
            session = self.create_session()
            if session != None:
                self.set_session(session)
        return self.get_session()

    def close_session(self):
        # Close session object shared by attack objects
        if self.session_exists():
            session = self.get_session()
            self.get_attack_class().close_session(session)
    # End: session methods


    def set_attack_class(self, attack_class):
        # Sets attack class to use when attacking
        if issubclass(attack_class, self._base_attack_type):
            self._attack_class = attack_class
        else:
            # f-string arent supported on py35 or less
            err_msg = "attack_class should be sub-class of '{}' not '{}'"
            err_msg = err_msg.format(
                type(self._base_attack_type).__name__,
                type(attack_class).__name__
            )
            raise TypeError(attack_class)

    def get_attack_class(self) -> Type[Attack]:
        # Returns attack class, raises error if not found
        if self._attack_class is not None:
            return self._attack_class
        else:
            err_msg = "Attack class is not available(required)"
            raise exceptions.MissingAttackType(err_msg)

    def _create_attack_object(self, data) -> Attack:
        # Creates attack object with set attack class
        # .get_attack_class() will raise error if not found
        attack_class = self.get_attack_class()
        return attack_class(self._target, data)

    def _add_default_produsers(self):
        # Adds default/startup produser within object __init__()
        self.add_producer_method("loop_all", self._producer_loop_all)
        self.add_producer_method("loop_some", self._producer_loop_some)



    def _get_current_producer_method(self):
        if self.should_optimise():
            producer_method = self._producer_loop_some
        else:
            producer_method = self._producer_loop_all
        return producer_method

    def get_producer_records(self) -> Iterable[forcetable.Record]:
        return self._get_current_producer_method()()



    def _attack_success_callback(self, attack_object, record):
        # Method is called when there is succcess in one of records.
        # Record is appended to to success records.
        self._success_records.append(record)

        if self._table.primary_field_exists():
            # Primary field is required in this block.
            # Optimisations are performed to speed bruteforce.
            primary_field = self._table.get_primary_field()
            primary_item = forcetable.extract_record_primary_item(
                record, primary_field
            )
            # Adds primary item to success and excluded records.
            self._success_primary_items.add(primary_item)
            # Adds success records grouped by primary item.
            if primary_item not in self._success_primary_items_map:
                self._success_primary_items_map[primary_item] = []
            self._success_primary_items_map[primary_item].append(record)



        if self.is_primary_optimised():
            # Performs actions based on primary item and record

            # Cancels producer/_consumer when maximum primary items have
            # been successfully bruteforced.
            # e.g when 4 usernames have been bruteforced successfully.
            if self._max_success_primary_items is not None:
                primary_items = self._success_primary_items
                if self._max_success_primary_items <= len(primary_items):
                    self._cancel_consumer_producer()

            # Excludes primary item and its record when maximum success
            # records have been reached.
            primary_records = self._success_primary_items_map[primary_item]
            if self._max_primary_success_records <= len(primary_records):
                self._excluded_primary_items.add(primary_item)


        if self._optimise and not self._table.primary_field_exists():
            # Single field behaves like primary field.
            if self._max_success_records is None and len(self._fields)==1:
                self._cancel_consumer_producer()


        # Cancels _consumer and producer on when max success records
        # is reached.
        if self._max_success_records is not None:
            # Not sure self._success_records will ever be larger
            # self._max_success_records.
            # Thats why '>=' was used as comparison operator.
            if len(self._success_records) >= self._max_success_records:
                # Cancels producer and _consumer
                self._cancel_consumer_producer()

        # Cancels _consumer and producer when _cancel_immediately is enabled.
        if self._cancel_immediately:
            self._cancel_consumer_producer()

    def _before_start(self):
        # Method called before starting bruteforce
        self._start_callback()

    def _after_start(self):
        # Method called before starting bruteforce
        self._done_callback()


    def _attack_failure_callback(self, attack_object, record):
        # Callback called when theres failure without error after attack attempt
        pass

    def _attack_error_callback(self, attack_object:Attack, record):
        # Callback called when theres error after attack attempt'''
        pass


    def _handle_attack_results(self, attack_object:Type[Attack], record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self._responce
        if attack_object.errors():
            self._attack_error_callback(attack_object, record)
        elif attack_object.failure():
            self._attack_failure_callback(attack_object, record)
        elif attack_object.success():
            self._attack_success_callback(attack_object, record)
        elif not attack_object.request_started():
            err_msg = "Request not started after starting request"
            raise exceptions.UnexpectedError(err_msg)
        else:
            err_msg = "Something is wrong with attack results"
            raise exceptions.UnexpectedError(err_msg)          
            


    def _cancel_consumer_producer(self):
        # Cancel both _consumer and producer
        self._cancel_producer()
        self._cancel_consumer()

    def cancel(self):
        # Cancels producer, _consumer and tasks to executed
        self._cancel_consumer_producer()

    def _task_done_callback(self, future: Future):
        # Called when task completes
        pass


    def _consumer_done_callback(self):
        # Called when _consumer completed
        self._consumer_completed = True

    def _producer_done_callback(self):
        # Called when producer completed
        self._producer_completed = True

    def running(self):
        # Returns True when attack is taking place
        return self._consumer_completed and self._producer_completed

    def _cancel_producer(self):
        # Requests producer to stop running
        self._producer_should_run = False
    

    def _cancel_consumer(self):
        # Requests producer to stop running
        self._consumer_should_run = False

    def _consumer_should_continue(self):
        return self._consumer_should_run

    def producer_should_continue(self):
        # Checks if producer should continue running
        return self._producer_should_run


    def _producer_loop_all(self):
        # Producer that loops through all records without skipping.
        producer_ = producer.LoopAllProducer(self._table)
        for record in producer_.get_items():
            yield record


    def _producer_loop_some(self):
        # Producer that loops through some records but would stop if
        # conditions are met.
        producer_ = producer.LoopSomeProducer(self._table)
        producer_.set_max_multiple_primary_items(
            self._max_multiple_primary_items)
        if self._producer_switch_callback:
            producer_.set_producer_switch_callback(
                self._producer_switch_callback
            )
        # Get copy for tracking changes
        excluded_primary_items = self._excluded_primary_items.copy()
        for record in producer_.get_items():
            # Check if success primary items has changed
            if excluded_primary_items != self._excluded_primary_items:
                # Update copy for tracking changes
                excluded_primary_items = self._excluded_primary_items.copy()
                # Update excluded primary items with success primary items
                producer_.add_excluded_primary_items(excluded_primary_items)
            yield record

    def producer(self):
        # Get and return records from producers
        for record in self.get_producer_records():
            if not self.producer_should_continue():
                break
            yield record
        self._producer_done_callback()


    def _get_next_producer_record(self):
        # Returns next record from producer
        while self._consumer_should_continue():
            try:
                return next(self._producer_records)
            except StopIteration:
                # Out of records
                break
        # Producer completed, ran out of records or _consumer completed.
        return None

    def _get_next_producer_records(self, max_records:int):
        # Returns list of next producer records
        records = []
        for _ in range(max_records):
            record = self._get_next_producer_record()
            if record != None:
                records.append(record)
            else:
                break
        return records


    def _handle_attack(self, record: Record):
        # Handles attack with provided record
        session = self.get_create_session() # get session for this thread
        with self._create_attack_object(record) as attack_object:
            if session != None:
                # offer attack object session before request
                # attack object should use the session during request
                attack_object.set_session(session)
            # .start_until_retries() the request(can take some time)
            attack_object.start_until_retries(
                self._consumer_should_continue
            )
            # handles results of the request
            self._handle_attack_results(attack_object, record)


    def _consumer(self):
        # Consumes records in producer and initiate attack
        raise NotImplementedError




class BForceParallel(BForceBase):
    '''Base class for performing bruteforce attack in parallel'''
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)
        # Stores _consumer tasks not yet completed
        self._current_tasks: Set[Future] = set()

        # Total independed tasks to run in parallel
        # Corresponds to attempts that will be executed concurrently
        self._max_parallel_tasks = 100

        # Defines how many workers to execute parallel tasks.
        # None means number whatever workers that can be created.
        self._max_workers = None

    def set_max_workers(self, max_workers):
        # Sets max workers for executor
        self._max_workers = max_workers

    def set_max_parallel_tasks(self, total):
        self._max_parallel_tasks = total

    def get_current_tasks(self):
        # Returns currently runningg tasks(fututes)
        return self._current_tasks

    def cancel_current_tasks(self):
        # Cancels current tasks
        for task in self._current_tasks:
            task.cancel()

    def cancel(self):
        # Cancels producer, _consumer and tasks to executed
        self._cancel_consumer_producer()
        self.cancel_current_tasks()

    def _task_done_callback(self, future: Future):
        # Called when task completes
        try:
            exception_ = future.exception()
            if exception_ and not hasattr(self, "__exception__200"):
                setattr(self, "__exception__200", True)
                self.cancel()
                raise exception_
        except (asyncio.CancelledError, futures.CancelledError):
            pass

    def _handle_attack_recursive(self, record):
        # Performs attack recoursively on record and other records.
        # When attack completes on record, another attack is started.
        # This continues until producer runs out of records.
        # This was first implemented by BForceAsync.
        self._handle_attack(record)
        while True:
            record = self._get_next_producer_record()
            if record != None:
                # Perform attack again on the record
                self._handle_attack(record)
            else:
                # Producer ran out of records
                break

    def _to_future(self, __callable:Callable) -> Future:
        # Returns future like object from callable object
        raise NotImplementedError

    def _handle_attack_future(self, record) -> Future:
        # Returns Future like object of self._handle_attack()
        def callback():
            self._handle_attack(record)
        return self._to_future(callback)

    def _handle_attack_recursive_future(self, record) -> Future:
        # Returns Future like object of self._handle_attack_recursive()
        def callback():
            self._handle_attack_recursive(record)
        return self._to_future(callback)

    def _wait_tasks(self, tasks:List[Future]):
        # Waits for tasks to complete and then returns
        for task in tasks:
            task.result()


    def _consumer(self):
        # Consumes items in records_queue
        tasks:Set[Future] = set()
        count = 0
        # The while loop can be replaced by Semaphore object
        while count < self._max_parallel_tasks:
            record = self._get_next_producer_record()
            if record != None:
                task = self._handle_attack_recursive_future(record)
                tasks.add(task)
                self._current_tasks.add(task)
                task.add_done_callback(self._current_tasks.discard)
                task.add_done_callback(self._task_done_callback)
            else:
                break
            count += 1
        # wait for the executed tasks to complete
        # completion of one task is start of another task
        if tasks:
            self._wait_tasks(tasks)
        self._consumer_done_callback()




class BForceExecutor(BForceParallel):
    '''Performs bruteforce concurrent attack using provided executor'''
    _base_attack_type = Attack
    _executor_type = Executor
    _local_type = threading.local
    _lock_type = threading.RLock

    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)
        self._executor: Executor = None
        self._local = self._local_type()
        self._lock = self._lock_type()
        self._executor_is_default = True

    def _get_next_producer_record(self):
        with self._lock:
            # Generators are not threadsafe.
            # ValueError: generator already executing
            return super()._get_next_producer_record()

    def set_executor(self, executor:Executor):
        # Sets executo to use e.g TheadPoolExecutor
        self._executor = executor

    def get_executor(self) -> Executor:
        # Returns pool executor e.g TheadPoolExecutor
        return self._executor

    def session_exists(self):
        # Checks if session exists for current thread
        return hasattr(self._local, "session")

    def set_session(self, session):
        # Sets session for curruent thread
        self._local.session = session

    def get_session(self):
        # Gets session for curruent thread
        if self.session_exists():
            return self._local.session
        return None

    def close_session(self):
        # Close session object shared by attack objects
        if not hasattr(self._local, "session_closed"):
            super().close_session()
            self._local.session_closed = True

    def _create_default_executor(self) -> Executor:
        # Creates executor object
        return self._executor_type(self._max_workers)

    def _create_get_executor(self):
        # Gets executor or create one if not set
        if self._executor == None:
            return self._create_default_executor()
        else:
            return self._executor

    def _to_future(self, __callable: Callable) -> Future:
        # Creates future from callable
        return self._executor.submit(__callable)

    
    def _before_start(self):
        # Called before .start()
        super()._before_start()
        self._executor_is_default = self._executor == None
        self._executor = self._create_get_executor()
    
    def _after_start(self):
        # Called after .start()
        super()._after_start()
        if self._max_workers is None: 
            max_workers = 50
        else: 
            max_workers = self._max_workers
        tasks = []
        for _ in range(max_workers):
            # Close session in each executor thread/proccess/etc
            tasks.append(self._executor.submit(self.close_session))
        if tasks:
            self._wait_tasks(tasks)
        # Cleans executor pool if not manually set.
        if not self._executor_is_default:
            self._executor.shutdown(True)

    def start(self):
        '''Starts attack into system identified by target'''
        self._before_start()
        try:
            self._consumer()
        finally:
            self._after_start()


class BForceThread(BForceExecutor):
    '''Performs bruteforce attack using threads'''
    _executor_type = ThreadPoolExecutor
    _local_type = threading.local
    _lock_type = threading.RLock


# class BForceProcess(BForceExecutor):
#     '''Performs bruteforce attack using processes'''
#     def __init__(self, target, table: Table, optimise=False) -> None:
#         super().__init__(target, table, optimise)
#         # RLock is preffered here over Lock
#         self._lock = multiprocessing.RLock()


#     def session_exists(self):
#         # Returns True if session exists
#         return "_session" in globals()

#     def set_session(self, session):
#         # Sets session object to be used by Attack objects
#         # Session is set globally for each process.
#         globals()["_session"] = session
        

#     def get_session(self):
#         if self.session_exists():
#             return globals()["_session"]
#         return None

#     def _create_default_executor(self) -> Executor:
#         # Creates process executor to execute tasks.
#         # Initialize was not set as get_create_executor handles
#         # everything about setting and creating executor.
#         return ProcessPoolExecutor(self._max_workers)

#     def _get_next_producer_record(self):
#         with self._lock:
#             # _get_next_producer_record() modifies some attributes.
#             # It needs to be under a lock(avoid data races)
#             return super()._get_next_producer_record()



class BForceAsync(BForceParallel):
    '''Performs attack on target with data from Ftable object(asyncio)'''
    _base_attack_type = AttackAsync 

    def __init__(self, target, table, optimise=False):
        super().__init__(target, table, optimise)
        self._current_tasks: Set[asyncio.Task]
        self.attack_class: Type[AttackAsync]


    # start: Session methods
    def session_exists(self):
        # Returns True if session object exists
        return hasattr(self, "_session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._session = session

    async def create_session(self):
        # Creates session object to be shared with attack objects
        attack_class = self.get_attack_class()
        try:
            # Ask attack class to create session
            session = await attack_class.create_session()
        except NotImplementedError:
            # Return None if attack class cant create session
            return None
        else:
            # Return session created by attack class
            return session

    def get_session(self):
        # Gets session object to be shared with attack objects
        if self.session_exists():
            return self._session

    async def get_create_session(self):
        if not self.session_exists():
            session = await self.create_session()
            if session != None:
                self.set_session(session)
        return self.get_session()

    async def close_session(self):
        # Close session object shared by attack objects
        if self.session_exists():
            session = self.get_session()
            # Session is now closed by attack class.
            attack_class = self.get_attack_class()
            await attack_class.close_session(session)
    # End: session methods


    async def _handle_attack_results(
        self, 
        attack_object: AttackAsync, 
        record: Record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self._responce
        if await attack_object.errors():
            self._attack_error_callback(attack_object, record)
        elif await attack_object.failure():
            self._attack_failure_callback(attack_object, record)
        elif await attack_object.success():
            self._attack_success_callback(attack_object, record)
        elif not attack_object.request_started():
            err_msg = "Request not started after starting request"
            raise exceptions.UnexpectedError(err_msg)
        else:
            err_msg = "Something is wrong with attack results"
            raise exceptions.UnexpectedError(err_msg)

    async def _handle_attack(self, record: Record):
        #print("run async def _handle_attack()")
        # Handles attack on attack class with asyncio support
        session = await self.get_create_session()
        async with self._create_attack_object(record) as attack_object:
            #print("after self._create_attack_object()")
            if session != None:
                # this line can speed request performance
                attack_object.set_session(session)
            # .start_until_retries() needs to be coroutine method
            await attack_object.start(
                self._consumer_should_continue
            )
            await self._handle_attack_results(attack_object, record)


    async def _handle_attack_recursive(self, record:Record):
        await self._handle_attack(record)
        while True:
            record = self._get_next_producer_record()
            if record != None:
                # Perform attack again on the record
                await self._handle_attack(record)
            else:
                # Stop performing any other tasks
                break

    def _to_future(self, __callable:Callable) -> Future:
        # Returns Task object from coroutine callable
        awaitable =  __callable() # should be awaitable
        return asyncio.ensure_future(awaitable)

    def _handle_attack_recursive_future(
        self, 
        record:Record) -> asyncio.Task:
        # Returns Task object from self._handle_attack_recursive()
        async def handle_attack_recursive():
            try: 
                await self._handle_attack_recursive(record)
            except asyncio.CancelledError:
                pass
        return self._to_future(handle_attack_recursive)

    async def _wait_tasks(self, tasks:List[asyncio.Task]):
        # Waits for tasks to complete and then returns
        await asyncio.gather(*tasks, return_exceptions=False)

    async def _consumer(self):
        # Consumes records in records producer
        tasks:Set[Future] = set()
        count = 0
        # Asynio does not have max workers(not limited like threads).
        # Minimum of max workers and current max parallel tasks is used.
        # Thats similar to how ThreadPoolExecutor/Executors behaves.
        if self._max_workers is not None:
            max_workers = self._max_workers
        else:
            max_workers = self._max_parallel_tasks
        max_parallel_tasks = min(max_workers, self._max_parallel_tasks)
        # The while loop can be replaced by Semaphore object
        while count < max_parallel_tasks:
            record = self._get_next_producer_record()
            if record != None:
                task = self._handle_attack_recursive_future(record)
                tasks.add(task)
                self._current_tasks.add(task)
                task.add_done_callback(self._task_done_callback)
            else:
                break
            count += 1
        # wait for the executed tasks to complete
        # completion of one task is start of another task
        if tasks:
            await self._wait_tasks(tasks)
        self._consumer_done_callback()


    async def start(self):
        self._before_start()
        try:
            await self._consumer()            
        finally:
            await self.close_session()
        self._after_start()



class BForceBlock(BForceBase):
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)  
        self._session: object
        
        
    def session_exists(self):
        # Returns True if session exists
        return hasattr(self, "_session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._session = session

    def get_session(self):
        # Gets session object
        if self.session_exists():
            return self._session
        return None

    def _consumer(self):
        for record in self._producer_records:
            if self._consumer_should_continue():
                self._handle_attack(record)
            else:
                break
        self._consumer_done_callback()

    def start(self):
        self._before_start()
        try:
            self._consumer()
        finally:
            self.close_session()
        self._after_start()


class BForce(BForceThread):
    # This class currently implemenets BForceThread.
    # Its not guaranteed to be that one in future.
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)       



if __name__ == "__main__":
    from .attacks import *

    # Prepare data for attack
    url = 'https://httpbin.org/post'
    usernames = ["david", "marry", "pearl"] * 1000
    passwords = ["1234", "0000", "th234"]

    # Creates fields for table
    usernames_col = Field('usernames', usernames)
    # Sets key name to use in record key in Table
    usernames_col.set_item_name("username")
    passwords_col = Field('passwords', passwords)
    passwords_col.set_item_name("password")

    table = Table()
    # Set common record to be shared by all records
    common_record = Record()
    common_record.add_item("submit", "login")
    table.set_common_record(common_record)
    # Add fields to table
    table.add_field(usernames_col)
    table.add_field(passwords_col)



    
    # starts attack
    start_time = time.time()

    test_obj = BForceAsync(url, table)
    test_obj.set_attack_class(WebAttackAsync)
    
    # see: https://stackoverflow.com/questions/45600579/
    # asyncio-event-loop-is-closed-when-getting-loop
    #asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_obj.start())
    #test_obj.start()

    duration = time.time() - start_time
    output_msg = "Downloaded {total} in {duration} seconds"
    output_msg = output_msg.format(
        total=len(usernames)*len(passwords),
        duration=duration
    )
    print(output_msg)
