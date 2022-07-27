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
import logging
import threading
import time
import itertools

import asyncio
from concurrent.futures import ThreadPoolExecutor
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

# Not used
#from .session import BForceSession
#from .session import BForceBlockSession
#from .session import BForceAsyncSession



class BForceBase():
    '''Base class for performing bruteforce on target with provided
    attack class and table object'''
    base_attack_class = Attack

    def __init__(self, target, table:Table, optimise=False) -> None:
        self._target = target
        self._table = table
        self._optimise = optimise
        self._primary_field = table.get_primary_field()
        self._fields = table.get_fields()

        # If True, pending tasks will be stopped on first success.
        # producer and consumer will also be stopped.
        self._cancel_immediately = False
        self._max_success_records = None

        # Changed callback when producer or consumer completes
        self._producer_completed = False
        self._consumer_completed = False

        # If False, producer would stop
        self._producer_should_run = True
        self._consumer_should_run = True

        # Primary items of cracked records
        self._success_primary_items = set()
        self._success_records = []


        # This sets maximum parallel primary items tasks
        # e.g multiples usernames can be executed at same time.
        self._max_parallel_primary_tasks = 1

        # producer records
        self._producer_records = iter(self.producer())

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

    def get_success_records(self):
        return self._success_records


    def create_session(self):
        # Creates session object to be shared with attack objects
        attack_class = self.get_attack_class()
        try:
            # Ask attack class to create session
            session = attack_class.create_session()
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
        # self._thread_local was created from threading.local()
        if not self.session_exists():
            session = self.create_session()
            if session != None:
                self.set_session(session)
        return self.get_session()

    def close_session(self):
        if self.session_exists():
            # Create fake attack object and set session
            attack_object = self.create_attack_object(Record())
            attack_object.set_session(self.get_session())
            # close the session set on the object
            attack_object.close_session()
    # End: session methods


    def set_attack_class(self, attack_class):
        # Sets attack class to use when attacking
        if issubclass(attack_class, self.base_attack_class):
            self.attack_class = attack_class
        else:
            # f-string arent supported on py35 or less
            err_msg = "attack_classis not subclass of " +\
                str(self.base_attack_class)
            raise Exception(err_msg, attack_class)

    def get_attack_class(self) -> Type[Attack]:
        # Returns attack class, raises error if not found
        if hasattr(self, "attack_class"):
            return self.attack_class
        else:
            err_msg = "attack_class not found"
            err_msg2 = "use set_attack_class() to set attack_class"
            raise AttributeError(err_msg, err_msg2)

    def create_attack_object(self, data) -> Attack:
        # Creates attack object with set attack class
        # .get_attack_class() will raise error if not found
        attack_class = self.get_attack_class()
        return attack_class(self._target, data)

    def _add_default_produsers(self):
        # Adds default/startup produser within object __init__()
        self.add_producer_method("loop_all", self._producer_loop_all)
        self.add_producer_method("loop_some", self._producer_loop_some)



    def get_current_producer_method(self):
        if self._optimise:
            producer_method = self._producer_loop_some
        else:
            producer_method = self._producer_loop_all
        return producer_method

    def get_producer_records(self) -> Iterable[forcetable.Record]:
        return self.get_current_producer_method()()

    def set_max_parallel_primary_tasks(self, total):
        self._max_parallel_primary_tasks = total



    def attack_success_callback(self, attack_object, record):
        # Callback called when theres success
        # Primary item of record is added to success primary values
        if self._table.primary_field_exists():
            primary_field = self._table.get_primary_field()
            primary_item = forcetable.get_record_primary_item(record, primary_field)
            # Use of lock can be removed on async version
            self._success_primary_items.add(primary_item)
            self._success_records.append(record)

        # Cancels consumer and producer on when max success records
        # is reached.
        if self._max_success_records != None:
            # Not sure self._success_records will ever be larger
            # self._max_success_records.
            # Thats why '>=' was used as comparison operator.
            if len(self._success_records) >= self._max_success_records:
                # Cancels producer and consumer
                self.cancel_consumer_producer()

        # Cancels consumer and producer when _cancel_immediately is True
        if self._cancel_immediately:
            self.cancel_consumer_producer()


    def attack_failure_callback(self, attack_object, record):
        # Callback called when theres failure without error after attack attempt
        pass

    def attack_error_callback(self, attack_object:Attack, record):
        # Callback called when theres error after attack attempt'''
        pass


    def handle_attack_results(self, attack_object:Type[Attack], record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self._responce
        if attack_object.errors():
            self.attack_error_callback(attack_object, record)
        elif attack_object.failure():
            self.attack_failure_callback(attack_object, record)
        elif attack_object.success():
            self.attack_success_callback(attack_object, record)
        else:
            err_msg = "Something went wrong while handling attack results"
            raise Exception(err_msg)          
            


    def cancel_consumer_producer(self):
        # Cancel both consumer and producer
        self.cancel_producer()
        self.cancel_consumer()

    def cancel(self):
        # Cancels producer, consumer and tasks to executed
        self.cancel_consumer_producer()
        self.cancel_current_tasks()

    def task_done_callback(self, future: Future):
        # Called when task completes
        pass


    def consumer_done_callback(self):
        # Called when consumer completed
        self._consumer_completed = True

    def producer_done_callback(self):
        # Called when producer completed
        self._producer_completed = True

    def running(self):
        # Returns True when attack is taking place
        return self._consumer_completed or self._producer_completed

    def cancel_producer(self):
        # Requests producer to stop running
        self._producer_should_run = False
    

    def cancel_consumer(self):
        # Requests producer to stop running
        self._consumer_should_run = False

    def consumer_should_continue(self):
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
        producer_.set_max_parallel_primary_tasks(
            self._max_parallel_primary_tasks
        )
        # Get copy for tracking changes
        success_primary_items = self._success_primary_items.copy()
        for record in producer_.get_items():
            # Check if success primary items has changed
            if success_primary_items != self._success_primary_items:
                # Update copy for tracking changes
                success_primary_items = self._success_primary_items.copy()
                # Update excluded primary items with success primary items
                producer_.set_excluded_primary_item(success_primary_items)
            yield record

    def producer(self):
        # Get and return records from producers
        for record in self.get_producer_records():
            if not self.producer_should_continue():
                break
            yield record
        self.producer_done_callback()


    def get_next_producer_record(self):
        # Returns next record from producer
        while self.consumer_should_continue():
            try:
                return next(self._producer_records)
            except StopIteration:
                # Out of records
                break
        # Producer completed and ran out of records
        # None means theres no any Records left
        return None

    def handle_attack(self, record: Record):
        # Handles attack with provided record
        session = self.get_create_session() # get session for this thread
        with self.create_attack_object(record) as attack_object:
            if session != None:
                # offer attack object session before request
                # attack object should use the session during request
                attack_object.set_session(session)
            # start the request(can take some time)
            attack_object.start_until_target_reached()
            # handles results of the request
            self.handle_attack_results(attack_object, record)


    def handle_attack_recursive(self, record):
        # Performs attack recoursively on record and other records.
        # When attack completes on record, another attack is started.
        # This continues until producer runs out of records.
        # This was first implemented by BForceAsync.
        self.handle_attack(record)
        while True:
            record = self.get_next_producer_record()
            if record != None:
                # Perform attack again on the record
                self.handle_attack(record)
            else:
                # Producer ran out of records
                break

    def consumer(self):
        # Consumes records in producer and initiate attack
        raise NotImplementedError




class BForceParallel(BForceBase):
    '''Base class for performing bruteforce attack in parallel'''
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)
        # Stores consumer tasks not yet completed
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

    def task_done_callback(self, future: Future):
        # Called when task completes
        self._current_tasks.discard(future)
        try:
            future.result()
        except Exception as e:
            # Cancels producer and consumer and re-raise exception
            # Cancelling current tasks would result in CancelError
            # Its better to leave running tasks and let them finish.
            if not hasattr(self, "exception_200"):
                # Exception will only be raised by once
                # only when self.exception_200 is not defied
                setattr(self, "exception_200", True)
                self.cancel_consumer_producer()
                raise e


    def to_future(self, __callable:Callable) -> Future:
        # Returns future like object from callable object
        raise NotImplementedError

    def handle_attack_recursive_future(self, record) -> Future:
        # Returns Future like object of self.handle_attack_recursive()
        def callback():
            self.handle_attack_recursive(record)
        return self.to_future(callback)

    def wait_tasks(self, tasks:List[Future]):
        # Waits for tasks to complete and then returns
        for task in tasks:
            task.result()


    def consumer(self):
        # Consumes items in records_queue
        tasks:Set[Future] = set()
        count = 0
        # The while loop can be replaced by Semaphore object
        while count < self._max_parallel_tasks:
            record = self.get_next_producer_record()
            if record != None:
                task = self.handle_attack_recursive_future(record)
                tasks.add(task)
                self._current_tasks.add(task)
                task.add_done_callback(self.task_done_callback)
            else:
                break
            count += 1
        # wait for the executed tasks to complete
        # completion of one task is start of another task
        if tasks:
            self.wait_tasks(tasks)
        self.consumer_done_callback()




class BForceExecutor(BForceParallel):
    '''Performs bruteforce concurrent attack using provided executor'''
    base_attack_class = Attack
    executor_class: Executor

    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)
        self._executor: Executor = None
        
        self._executor_is_default = True

    def set_executor(self, executor:Executor):
        # Sets executo to use e.g TheadPoolExecutor
        self._executor = executor

    def get_executor(self) -> Executor:
        # Returns pool executor e.g TheadPoolExecutor
        return self._executor

    def create_default_executor(self) -> Executor:
        # Creates executor object
        raise NotImplementedError

    def create_get_executor(self):
        # Gets executor or create one if not set
        if self._executor == None:
            return self.create_default_executor()
        else:
            return self._executor

    def to_future(self, __callable: Callable) -> Future:
        return self._executor.submit(__callable)

    def start(self):
        '''Starts attack into system identified by target'''
        self._executor_is_default = self._executor == None
        self._executor = self.create_get_executor()
        self.consumer()
        if not self._executor_is_default:
            self._executor.shutdown(True)
        self.close_session()


class BForceThread(BForceExecutor):
    '''Performs bruteforce attack using threads'''
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)
        self._thread_local = threading.local()
        self._lock = threading.Lock()


    def session_exists(self):
        # Returns True if session exists
        return hasattr(self._thread_local, "session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._thread_local.session = session

    def get_session(self):
        if self.session_exists():
            return self._thread_local.session
        return None
        

    def create_default_executor(self) -> Executor:
        return ThreadPoolExecutor(self._max_parallel_tasks)

    def get_next_producer_record(self):
        with self._lock:
            return super().get_next_producer_record()



class BForceAsync(BForceParallel):
    '''Performs attack on target with data from Ftable object(asyncio)'''
    base_attack_class = AttackAsync 

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
            # Create fake attack object and set session
            attack_object = self.create_attack_object(Record())
            attack_object.set_session(self.get_session())
            # close the session se on the object
            await attack_object.close_session()
    # End: session methods


    async def handle_attack_results(
        self, 
        attack_object: AttackAsync, 
        record: Record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self._responce
        if await attack_object.errors():
            self.attack_error_callback(attack_object, record)
        elif await attack_object.failure():
            self.attack_failure_callback(attack_object, record)
        elif await attack_object.success():
            self.attack_success_callback(attack_object, record)
        else:
            err_msg = "Something went wrong while handling attack results"
            raise Exception(err_msg)

    async def handle_attack(self, record: Record):
        #print("run async def handle_attack()")
        # Handles attack on attack class with asyncio support
        session = await self.get_create_session()
        async with self.create_attack_object(record) as attack_object:
            #print("after self.create_attack_object()")
            if session != None:
                # this line can speed request performance
                attack_object.set_session(session)
            # .start() needs to be coroutine method
            await attack_object.start_until_target_reached()
            await self.handle_attack_results(attack_object, record)


    async def handle_attack_recursive(self, record:Record):
        await self.handle_attack(record)
        while True:
            record = self.get_next_producer_record()
            if record != None:
                # Perform attack again on the record
                await self.handle_attack(record)
            else:
                # Stop performing any other tasks
                break

    def to_future(self, __callable:Callable) -> Future:
        # Returns Task object from coroutine callable
        awaitable =  __callable() # should be awaitable
        return asyncio.ensure_future(awaitable)

    def handle_attack_recursive_future(
        self, 
        record:Record) -> asyncio.Task:
        # Returns Task object from self.handle_attack_recursive()
        async def callback():
            await self.handle_attack_recursive(record)
        return self.to_future(callback)

    async def wait_tasks(self, tasks:List[asyncio.Task]):
        # Waits for tasks to complete and then returns
        await asyncio.gather(*tasks, return_exceptions=False)

    async def consumer(self):
        # Consumes items in records_queue
        tasks:Set[Future] = set()
        count = 0
        # The while loop can be replaced by Semaphore object
        while count < self._max_parallel_tasks:
            record = self.get_next_producer_record()
            if record != None:
                task = self.handle_attack_recursive_future(record)
                tasks.add(task)
                self._current_tasks.add(task)
                task.add_done_callback(self.task_done_callback)
            else:
                break
            count += 1
        # wait for the executed tasks to complete
        # completion of one task is start of another task
        if tasks:
            await self.wait_tasks(tasks)
        self.consumer_done_callback()


    async def start(self):
        await self.consumer()
        await self.close_session()



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

    def consumer(self):
        for record in self._producer_records:
            if self.consumer_should_continue():
                self.handle_attack(record)
            else:
                break
        self.consumer_done_callback()

    def start(self):
        self.consumer()


class BForce(BForceThread):
    # This class currently implemenets BForceThread.
    # Its not guaranteed to be that one in future.
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)       
# format = "%(asctime)s: %(message)s"
# logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")


if __name__ == "__main__":
    from .attacks import *

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

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
