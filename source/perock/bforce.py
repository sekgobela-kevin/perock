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

# Each class in the modue contain methods that could be split to other classes.
# Methods involving session and producer can be made their own classes.
# Theres also a need for base class for BForce classes.
# Its also a pain to maintain async version of BForce class.

# This module has grecordn beyond what was planned.
# It was supposed to contain one class but now has 3 classes.
# Each class implements methods their own way which adds even more lines.


from typing import Callable, Dict, Iterable, List, Set, Type
import logging
import queue
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


# asyncio.to_thread() is New in Python version 3.9.
# see https://docs.python.org/3/library/asyncio-task.html#id10
from .util import to_thread


format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

class BForce():
    '''Performs attack on target with data from Table object(threaded)'''
    base_attack_class = Attack

    def __init__(self, target, table:Table, optimise=True) -> None:
        self._target = target
        self._table = table
        self._optimise = optimise
        self._primary_field = table.get_primary_field()
        self._fields = table.get_fields()

        # If True, pending tasks will be stopped on first success.
        # producer and consumer will also be stopped.
        self._cancel_immediately = False
        self._max_success_records = None

        # Total independed tasks to run
        # Corresponds to requests that will be executed concurrently
        self.total_tasks = 500
        # Threads to use on self.total_tasks
        self.total_threads = None
        
        # store thread specific attributes
        # e.g session object
        self._thread_local = threading.local()
        self._lock = threading.Lock()

        # Changed callback when producer or consumer completes
        self.producer_completed = False
        self.consumer_completed = False

        # If False, producer would stop
        self.producer_should_run = True
        self.consumer_should_run = True

        # Primary items of cracked records
        self._success_primary_items = set()
        self._success_records = []


        # Stores consumer tasks not yet completed
        self._current_tasks: Set[Future] = set()

        self.executor: Executor = None
        self.max_workers = None

        # This sets maximum parallel primary items tasks
        # e.g multiples usernames can be executed at same time.
        self._max_parallel_primary_tasks = 5

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

    def set_executor(self, executor):
        # Sets executo to use e.g TheadPoolExecutor
        self.executor = executor

    def get_executor(self) -> Executor:
        # Returns pool executor e.g TheadPoolExecutor
        return self.executor

    def get_success_records(self):
        return self._success_records

    def set_max_workers(self, max_workers):
        # Sets max workers for executor
        self.max_workers = max_workers

    def create_or_get_executor(self):
        # Gets executor or create one if not set
        if self.executor == None:
            return ThreadPoolExecutor(self.max_workers)
        else:
            return self.executor

    
    def set_total_threads(self, total):
        self.total_threads = total
        self.set_max_workers(total)

    def set_max_parallel_tasks(self, total):
        self.total_tasks = total


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
        return hasattr(self._thread_local, "session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._thread_local.session = session

    def get_session(self):
        # Gets session object to be shared with attack objects
        # Realise the use of thread_local
        # self._thread_local was created from threading.local()
        if not self.session_exists():
            try:
                session = self.create_session()
            except NotImplementedError:
                return None
            else:
                self.set_session(session)
        # Returned session is thread safe
        return self._thread_local.session

    def close_session(self):
        if hasattr(self._thread_local, "session"):
            # Create fake attack object and set session
            attack_object = self.create_attack_object(Record())
            attack_object.set_session(self.get_session())
            # close the session se on the object
            attack_object.close_session()
    # End: session methods


    def set_attack_class(self, attack_class):
        # Sets attack class to use when attacking
        if issubclass(attack_class, self.base_attack_class):
            self.attack_class = attack_class
        else:
            err_msg = f"{attack_class} is not subclass of {self.base_attack_class}"
            raise Exception(err_msg)

    def get_attack_class(self) -> Type[Attack]:
        # Returns attack class, raises error if not found
        if hasattr(self, "attack_class"):
            return self.attack_class
        else:
            err_msg = "attack_class not found"
            err_msg2 = "use set_attack_class() to set attack_class"
            raise AttributeError(err_msg, err_msg2)

    def attack_class_async(self):
        # Checks if attack class is asynchronous
        attack_class = self.get_attack_class()
        return issubclass(attack_class, AttackAsync)

    def create_attack_object(self, data) -> Attack:
        # Creates attack object with set attack class
        # .get_attack_class() will raise error if not found
        attack_class = self.get_attack_class()
        return attack_class(self._target, data)

    def _add_default_produsers(self):
        # Adds default/startup produser within object __init__()
        self.add_producer_method("loop_all", self._producer_loop_all)
        self.add_producer_method("loop_some", self._producer_loop_some)

    @staticmethod
    def clear_queue(queue_object):
        # Clear the queue and break from the loop
        while True:
            try:
                queue_object.get(block=False)
            except queue.Empty:
                break


    def _producer_loop_all(self):
        '''
        Producer that loops through all records but checks before
        putting record to tasks queue. 

        This is great if primary field is not provided or need more 
        control on wheather record be added to tasks queue. This method
        will loop through all Records objects in Table object.

        It is fast but not faster as it loops through all Records which
        could be millions in size depending on total fields and their 
        sizes. But it guarantees that each record will be checked unlike
        `_producer_loop_some(self)` which will skip records.

        Condition can be checking if record is already cracked successfully 
        or already attempted. Conditions are defined by 
        `self.should_put_record(record)` which should return True if record be
        put to tasks.
        '''
        producer_ = producer.LoopAllProducer(self._table)
        for record in producer_.get_items():
            if not self.producer_should_continue():
                break
            yield record

    def _producer_loop_some(self):
        '''
        Producer that loops through some records but would stop if
        conditions are met. 

        This method requires that Table object contain primary field
        if not please use `._producer_loop_all()` method. Any item in
        primary field will only be tried until conditions are met. If 
        conditions are met it terminate and begin with another item of 
        primary field.

        This method is similar to `self._producer_loop_all()` but its just
        that it quits if conditions are right and it will never perform
        check on same records with that primary field. Think of it as 
        optimised version of `self._producer_loop_all()` which does not
        loop on everything.

        This producer is worth it for usernames and passwords attack were
        username is valid with only single password. If thats not neccessary
        then its better to use `self._producer_loop_all()`.

        Condition can be checking if record is already cracked successfully 
        or already attempted. Conditions are defined by 
        `self.should_put_record(record)` which should return True if record be
        put to tasks.
        '''
        producer_ = producer.LoopSomeProducer(self._table)
        producer_.set_max_parallel_primary_tasks(
            self._max_parallel_primary_tasks
        )
        # Get copy for tracking changes
        success_primary_items = self._success_primary_items.copy()
        for record in producer_.get_items():
            if not self.producer_should_continue():
                break
            # Check if success primary items has changed
            if success_primary_items != self._success_primary_items:
                # Update copy for tracking changes
                success_primary_items = self._success_primary_items.copy()
                # Update excluded primary items with success primary items
                producer_.set_excluded_primary_item(success_primary_items)
            yield record

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

    def producer(self):
        '''
        Producer method that put records to tasks queue from 
        Ftable object

        This ethod may call other producer methods that perform task
        of putting Record objects to queue. Wheather Record object will be put
        to tasks queue would depend on producer method called.

        Some of methods that may be called may include `_producer_loop_all(self)`
        and `_producer_loop_some(self)`. `should_put_record(record)` is may be 
        called by producer methods to decide if Record object should be put
        to tasks queue.

        Note that some Record objects can be skipped, `_producer_loop_some(self)`
        also skips Record objects without even checking or creating them. Each
        producer method behave differently and have their pros and cons.
        '''
        # Error like missing primary key expected
        try:
            records = self.get_producer_records()
            for record in records:
                self.records_queue.put(record)
        except Exception as e:
            # Raise original exception
            raise e
        finally:
            # Alert that producer finished
            self.producer_done_callback()



    def records_queue_elements(self, size=None, timeout=0.2) -> List[Record]:
        # Accesses size items from records_queue
        # If size is None, accesses from current qsize()
        if size == None:
            size = self.records_queue.qsize()
        table = []
        count = 0
        while count < size:
            try:
                # Get record if available in timeout
                record = self.records_queue.get(timeout=timeout)
            except queue.Empty:
                # Break the loop if failed to get record
                # That may mean producer finished running
                break
            else:
                table.append(record)  
            count += 1
        # If table is empty, records_queue may be empty
        # Producer may have stopped or timeout is too small
        return table



    def attack_success_callback(self, attack_object, record):
        # Callback called when theres success
        # Primary item of record is added to success primary values
        logging.info("Target/system was unlocked: " + str(record))
        if self._table.primary_field_exists():
            primary_field = self._table.get_primary_field()
            primary_item = forcetable.get_record_primary_item(record, primary_field)
            # Use of lock can be removed on async version
            with self._lock:
                self._success_primary_items.add(primary_item)
        with self._lock:
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
        logging.info(attack_object.get_responce_message())


    def handle_attack_results(self, attack_object:Type[Attack], record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self.responce
        if attack_object.errors():
            self.attack_error_callback(attack_object, record)
        elif attack_object.failure():
            self.attack_failure_callback(attack_object, record)
        elif attack_object.success():
            self.attack_success_callback(attack_object, record)
        else:
            err_msg = "Something went wrong while handling attack results"
            raise Exception(err_msg)          
            


    def handle_attack(self, record):
        # Handles attack on thread
        # Use it only on threads as .start() would block
        # This method can be passed to thread pool executor
        session = self.get_session() # get session for this thread
        with self.create_attack_object(record) as attack_object:
            if session != None:
                # offer attack object session before request
                # attack object should use the session during request
                attack_object.set_session(session)
            # start the request(can take some time)
            attack_object.start()
            # handles results of the request
            self.handle_attack_results(attack_object, record)

    def handle_attacks(self, executor, table):
        # Performs attack on provided table using threads
        # Useful if attack class not using asyncio
        futures: List[asyncio.Future] = []
        for record in table:
            future = executor.submit(self.handle_attack, record)
            futures.append(future)
        #concurrent.futures.wait(futures, timeout=self.tasks_wait)
        return futures

    def get_current_tasks(self):
        # Returns currently runningg tasks(fututes)
        return self._current_tasks

    def cancel_current_tasks(self):
        # Cancels current tasks
        for task in self._current_tasks:
            task.cancel()

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
        self.semaphore.release()
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



    def consumer_done_callback(self):
        # Called when consumer completed
        self.consumer_completed = True

    def producer_done_callback(self):
        # Called when producer completed
        self.producer_completed = True

    def running(self):
        # Returns True when attack is taking place
        return self.consumer_completed or self.producer_completed

    def cancel_producer(self):
        # Requests producer to stop running
        self.producer_should_run = False
        try:
            # Get item from records_queue to give producer opportunity to stop.
            # This applies incase producer has stopped
            self.records_queue.get(block=False)
        except queue.Empty:
            pass

    def cancel_consumer(self):
        # Requests producer to stop running
        self.consumer_should_run = False


    def consumer_should_continue(self):
        # Checks if consumer should continue running
        if not self.consumer_should_run:
            return False
        elif self.records_queue.empty() and self.producer_completed:
            # Producer completed and its items were consumed
            return False
        else :
            return True

    def producer_should_continue(self):
        # Checks if producer should continue running
        return self.producer_should_run


    def consumer_get_queue_record(self):
        # Gets Frecord from records queue for consumer
        while self.consumer_should_continue():
            # wait until producer put record or consumer should stop
            try:
                return self.records_queue.get(block=False)
            except queue.Empty:
                # continue to check if consumer should run
                # we cannot just terminate the loop.
                # producer may put the at any moment.
                continue
        # Producer completed and ran out of Frecords
        # None means theres no any Records left
        return None

    def consumer(self, executor=None):
        # Consumes items in records_queue
        if executor == None:
            executor = self.create_or_get_executor()
        while True:
            # This will block until one of futures/tasks complete
            self.semaphore.acquire()
            # This will wait until record is available
            # Returns None if consumer should not continue running
            record = self.consumer_get_queue_record()
            if record != None:
                future = executor.submit(self.handle_attack, record)
                self._current_tasks.add(future)
                future.add_done_callback(self.task_done_callback)
            else:
                # Consumer should stop as it ran out of records
                break
        self.close_session()
        self.consumer_done_callback()


    def start(self):
        '''Starts attack into system identified by target'''
        # setup semaphore and queue at start
        # sets value and maxsize to total_tasks
        self.semaphore = threading.Semaphore(self.total_tasks)
        self.records_queue = queue.Queue(self.total_tasks)

        futures = []
        executor = self.create_or_get_executor()
        futures.append(executor.submit(self.producer))
        futures.append(executor.submit(self.consumer, executor))
        for future in futures:
            # Raises exception if there was error
            future.result()
        if self.executor == None:
            executor.shutdown(True)



        
        
class BForceAsync(BForce):
    '''Performs attack on target with data from Ftable object(asyncio)'''
    base_attack_class = AttackAsync 

    def __init__(self, target, table, optimise=False):
        super().__init__(target, table, optimise)
        self._current_tasks: Set[asyncio.Task]
        self.attack_class: Type[AttackAsync]

    #def create_attack_object(self, data) -> AttackAsync: 
    #    ...

    # start: Session methods
    def session_exists(self):
        # Returns True if session object exists
        return hasattr(self, "session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self.session = session

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

    async def get_session(self):
        # Gets session object to be shared with attack objects
        # Realise that thread_local wasnt used
        # Asyncio runs tasks in same thread so session is thread safe
        # We also have choice of when to switch task compared to threads
        if not self.session_exists():
            try:
                session = await self.create_session()
            except NotImplementedError:
                return None
            else:
                self.set_session(session)
        # Not thread safe but safe with asyncio
        return self.session


    async def close_session(self):
        # Close session object shared by attack objects
        if self.session_exists():
            # Create fake attack object and set session
            attack_object = self.create_attack_object(Record())
            attack_object.set_session(await self.get_session())
            # close the session se on the object
            await attack_object.close_session()
    # End: session methods

    async def producer_coroutine(self):
        # Creates producer from producer() on different thread
        return await to_thread(self.producer)

    def producer_task(self):
        # Creates async task to producer method
        return asyncio.create_task(self.producer_coroutine)

    async def handle_attack_results(
        self, 
        attack_object: AttackAsync, 
        record: Record):
        # Handles results of attack on attack object
        # start() was already called and finished
        # responce can be accessed with self.responce
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
        session = await self.get_session()
        async with self.create_attack_object(record) as attack_object:
            #print("after self.create_attack_object()")
            if session != None:
                # this line can speed request performance
                attack_object.set_session(session)
            # .start() needs to be coroutine method
            await attack_object.start()
            await self.handle_attack_results(attack_object, record)

    async def handle_attacks(self, table: Iterable[Type[Record]]):
        # Performs attack on provided table using threads
        # Useful if attack class not using asyncio
        tasks:List[asyncio.Task] = []
        for record in table:
            awaitable =  self.handle_attack(record)
            task = asyncio.ensure_future(awaitable)
            tasks.append(task)
            #task.add_done_callback(background_tasks.discard)
        # asyncio.gather should be future object
        await asyncio.gather(*tasks, return_exceptions=False)


    async def handle_attack_recursive(self, record):
        await self.handle_attack(record)
        while True:
            record = self.consumer_get_queue_record()
            if record != None:
                # Perform attack again on the record
                await self.handle_attack(record)
            else:
                # Stop performing any other tasks
                break

    async def handle_attacks_recursive(self, table):
        tasks:Set[asyncio.Task] = set()
        for record in table:
            awaitable =  self.handle_attack_recursive(record)
            task = asyncio.ensure_future(awaitable)
            tasks.add(task)
            self._current_tasks.add(task)
            task.add_done_callback(tasks.discard)
            task.add_done_callback(self.task_done_callback)
        # run tasks asynchronously and wait for completion
        await asyncio.gather(*tasks, return_exceptions=False)


    async def consumer(self):
        # Consumes items in records_queue
        tasks:Set[asyncio.Task] = set()
        count = 0
        # The while loop can be replaced by Semaphore object
        while count < self.total_tasks:
            record = self.consumer_get_queue_record()
            if record != None:
                awaitable =  self.handle_attack_recursive(record)
                task = asyncio.create_task(awaitable)
                tasks.add(task)
                self._current_tasks.add(task)
                task.add_done_callback(tasks.discard)
                task.add_done_callback(self.task_done_callback)
            else:
                break
            count += 1
        # wait for the executed tasks to complete
        # completion of one task is start of another task
        if tasks:
            await asyncio.wait(tasks)
        self.consumer_done_callback()
        await self.close_session()


    async def start(self):
        # setup semaphore and queue at start
        # sets value and maxsize to total_tasks
        self.semaphore = threading.Semaphore(self.total_tasks)
        self.records_queue = queue.Queue(self.total_tasks)
        # producer and consumer as awaitables
        awaitables = [self.producer_coroutine(), self.consumer()]
        tasks = []
        for awaitable in awaitables:
            task = asyncio.ensure_future(awaitable)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=False)



class BForceBlock(BForce):
    def __init__(self, target, table: Table, optimise=False) -> None:
        super().__init__(target, table, optimise)

    def producer_should_switch(self, record):
        if len(self._fields) == 1:
            if self._success_records:
                return True
        else:
            return not self.should_put_record(record)

    def producer(self):
        # Get and return records from producers
        for record in self.get_producer_records():
            yield record
        self.producer_done_callback()

    def producer_should_continue(self):
        return self.producer_should_run

    def consumer_should_continue(self):
        return self.consumer_should_run

    def handle_attack(self, record):
        attack_object = self.create_attack_object(record)
        # Start a request with target
        attack_object.start()
        self.handle_attack_results(attack_object, record)

    def consumer(self):
        for record in self.producer():
            self.handle_attack(record)
        self.producer_done_callback()
        self.consumer_done_callback()

    def start(self):
        self.consumer()

        

if __name__ == "__main__":
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
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_obj.start())
    #test_obj.start()

    duration = time.time() - start_time
    print(f"Downloaded {len(usernames)*len(passwords)} in {duration} seconds")
