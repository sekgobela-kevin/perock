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

from typing import Callable, Dict, List, Set, Type
import logging
import queue
import threading
import time
import asyncio
from concurrent.futures import InvalidStateError, ThreadPoolExecutor
from concurrent.futures import Future
#from concurrent.futures import as_completed
#import concurrent.futures


from .attack import Attack
from .attack import AttackAsync

from .forcetable import FColumn
from .forcetable import FRow
from .forcetable import FTable

from . import forcetable


# asyncio.to_thread() is New in Python version 3.9.
# see https://docs.python.org/3/library/asyncio-task.html#id10
from .util import to_thread


class BForce():
    '''Performs attack on target with data from FTable object(threaded)'''
    def __init__(self, target, ftable:FTable) -> None:
        self.target = target
        self.ftable = ftable
        self.primary_column = ftable.get_primary_column()

        # Total independed tasks to run
        # Corresponds to requests that will be executed concurrently
        self.total_tasks = 500
        # Threads to use on self.total_tasks
        self.total_threads = 10
        # Time to wait to complete self.total_tasks
        self.tasks_wait = 100 

        # Time to wait on each task
        self.task_wait = 0 #10
        # Time to for item from producer
        self.row_put_wait = 0
        self.row_get_wait = 0.2

        # store thread specific attributes
        # e.g session object
        self.thread_local = threading.local()
        self.lock = threading.Lock()

        # Changed callback when producer or consumer completes
        self.producer_completed = False
        self.consumer_completed = False

        # If False, producer would stop
        self.producer_should_run = True

        # Primary items of cracked rows
        self.success_primary_items = set()

        # Stores producer methods and their names
        self.producers_map: Dict[str, Callable]
        self.producers_map = dict() # {'method_name': method}
        # Set the current current producer name
        self.current_producer_name = 'producer_loop_all'

        # Adds default/startup producer methods to 
        self._add_default_produsers()

        # Stores consumer tasks not yet completed
        self.current_tasks: Set[Future] = set()

    
    def set_total_threads(self, total):
        self.total_threads = total

    def set_total_tasks(self, total):
        self.total_tasks = total

    def set_task_wait(self, seconds):
        self.task_wait = seconds

    def set_input_wait(self, seconds):
        self.input_wait = seconds

    def set_output_wait(self, seconds):
        self.output_wait = seconds

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

    def close_session(self):
        if hasattr(self.thread_local, "session"):
            attack_class = self.get_attack_class()
            attack_class.close_session(self.session)


    def get_session(self):
        # Gets session object to be shared with attack objects
        # Realise the use of thread_local
        # self.thread_local was created from threading.local()
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = self.create_session()
            #if session != None:
            #    self.thread_local.session = session
        # Returned session is thread safe
        return self.thread_local.session

    def set_attack_class(self, attack_class):
        # Sets attack class to use when attacking
        self.attack_class = attack_class

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
        return isinstance(attack_class, AttackAsync)

    def create_attack_object(self, data) -> Attack:
        # Creates attack object with set attack class
        # .get_attack_class() will raise error if not found
        attack_class = self.get_attack_class()
        return attack_class(self.target, data)

    def should_put_row(self, frow):
        # Returns True if row should be put to queue
        # logic to decide if row should be put to queque
        if self.ftable.primary_column_exists():
            return not forcetable.row_primary_included(
                frow, 
                self.primary_column, 
                self.success_primary_items
            )
        # Put all rows to queue if primary column not detected
        return True


    def add_producer_method(self, name, method):
        '''Adds producer method collection of producer methods'''
        self.producers_map[name] = method

    def get_producer_methods(self) -> List[Callable]:
        '''Returns collection of producer methods'''
        return list(self.producers_map.values())

    def get_producer_method(self, producer_name) -> Callable:
        '''Returns producer method from producer name'''
        try:
            return self.producers_map[producer_name]
        except KeyError:
            err_msg = f"Producer with name '{producer_name}' not found"
            raise KeyError(err_msg)

    def set_current_producer(self, producer_name):
        '''Set current producer by its name'''
        if producer_name in self.producers_map:
            self.current_producer_name = producer_name
        else:
            err_msg = f"Producer with name '{producer_name}' not found"
            raise KeyError(err_msg)

    def get_current_producer(self):
        '''Returns current producer name'''
        return self.current_producer_name

    def get_current_producer_method(self):
        '''Returns current producer method'''
        return self.get_producer_method(self.current_producer_name)

    def _add_default_produsers(self):
        # Adds default/startup produser within object __init__()
        self.add_producer_method("loop_all", self.producer_loop_all)
        self.add_producer_method("loop_some", self.producer_loop_some)

    @staticmethod
    def clear_queue(queue_object):
        # Clear the queue and break from the loop
        while True:
            try:
                queue_object.get(block=False)
            except queue.Empty:
                break


    def producer_loop_all(self):
        '''
        Producer that loops through all frows but checks before
        putting frow to tasks queue. 

        This is great if primary column is not provided or need more 
        control on wheather frow be added to tasks queue. This method
        will loop through all FRows objects in FTable object.

        It is fast but not faster as it loops through all FRows which
        could be millions in size depending on total columns and their 
        sizes. But it guarantees that each frow will be checked unlike
        `producer_loop_some(self)` which will skip frows.

        Condition can be checking if frow is already cracked successfully 
        or already attempted. Conditions are defined by 
        `self.should_put_row(frow)` which should return True if frow be
        put to tasks.
        '''
        for frow in self.ftable:
            #print(self.should_put_row(frow), self.success_primary_items)
            if not self.producer_should_run:
                # Clear the queue and break from the loop
                self.clear_queue(self.ftable_queue)
                break
            elif self.should_put_row(frow):
                # queue.put() will block if queue is already full
                self.ftable_queue.put(frow)

    def producer_loop_some(self):
        '''
        Producer that loops through some frows but would stop if
        conditions are met. 

        This method requires that FTable object contain primary column
        if not please use `.producer_loop_all()` method. Any item in
        primary column will only be tried until conditions are met. If 
        conditions are met it terminate and begin with another item of 
        primary column.

        This method is similar to `self.producer_loop_all()` but its just
        that it quits if conditions are right and it will never perform
        check on same frows with that primary column. Think of it as 
        optimised version of `self.producer_loop_all()` which does not
        loop on everything.

        This producer is worth it for usernames and passwords attack were
        username is valid with only single password. If thats not neccessary
        then its better to use `self.producer_loop_all()`.

        Condition can be checking if frow is already cracked successfully 
        or already attempted. Conditions are defined by 
        `self.should_put_row(frow)` which should return True if frow be
        put to tasks.
        '''
        if self.ftable.primary_column_exists():
            primary_column = self.ftable.get_primary_column()
            primary_items = self.ftable.get_primary_items()
            # other_columns needs to exclude primary column
            other_columns = self.ftable.get_columns()
            other_columns.discard(primary_column)
            # This one is the common row
            common_row = self.ftable.get_common_row()
            # Loop each of primary column items
            for primary_item in primary_items:
                # Creates column for primary column
                # Name of column is taken from primary column
                column = FColumn(primary_column.get_name(), [primary_item])
                column.set_item_name(primary_column.get_item_name())
                # Merge the column with other columns
                columns = other_columns.union([column])
                # Creates rows the columns
                frows = FTable.columns_to_rows(columns, common_row)
                for frow in frows:
                    if not self.producer_should_run:
                        # Clear remaining queue items and return method
                        # Consumer may continue running
                        self.clear_queue(self.ftable_queue)
                        return
                    elif self.should_put_row(frow):
                        # Put frow to queque
                        self.ftable_queue.put(frow)
                    else:
                        # Clear remaining FRows and try next primary item
                        # Consumer may have captured the FRows
                        self.clear_queue(self.ftable_queue)
                        break
                        
        else:
            err_msg = f"Current producer requires primary column"
            raise Exception(err_msg)

    def producer(self):
        '''
        Producer method that put frows to tasks queue from 
        Ftable object

        This ethod may call other producer methods that perform task
        of putting FRow objects to queue. Wheather FRow object will be put
        to tasks queue would depend on producer method called.

        Some of methods that may be called may include `producer_loop_all(self)`
        and `producer_loop_some(self)`. `should_put_row(frow)` is may be 
        called by producer methods to decide if FRow object should be put
        to tasks queue.

        Note that some FRow objects can be skipped, `producer_loop_some(self)`
        also skips FRow objects without even checking or creating them. Each
        producer method behave differently and have their pros and cons.
        '''
        # Gets and call current producer method
        self.get_current_producer_method()()
        self.producer_done_callback()



    def ftable_queue_elements(self, size=None, timeout=0.2) -> List[FRow]:
        # Accesses size items from ftable_queue
        # If size is None, accesses from current qsize()
        if size == None:
            size = self.ftable_queue.qsize()
        ftable = []
        count = 0
        while count < size:
            try:
                # Get frow if available in timeout
                frow = self.ftable_queue.get(timeout=timeout)
            except queue.Empty:
                # Break the loop if failed to get frow
                # That may mean producer finished running
                break
            else:
                ftable.append(frow)  
            count += 1
        # If ftable is empty, ftable_queue may be empty
        # Producer may have stopped or timeout is too small
        return ftable



    def success_callback(self, attack_object, frow):
        '''Callback called when theres success'''
        # Primary item of row is added to success primary values
        if self.ftable.primary_column_exists():
            primary_column = self.ftable.get_primary_column()
            primary_item = forcetable.get_row_primary_item(frow, primary_column)
            # Use of lock can be removed on async version
            with self.lock:
                self.success_primary_items.add(primary_item)

    def handle_attack_results(self, attack_object:Type[Attack], frow):
        # Handles results of attack on attack object
        # start_request() was already called and finished
        # responce can be accessed with self.responce
        if not attack_object.errors():
            logging.info("Attack sucessful: " + str(frow))
            self.success_callback(attack_object, frow)
        elif attack_object.request_failed:
            logging.info("Request filed to start: " + 
            attack_object.request_fail_msg[:100])
        elif attack_object.client_errors():
            logging.info("Errors due to client: " + 
            attack_object.responce_err_msg[:100])
        elif attack_object.target_errors():
            logging.info("Errors on target: " + 
            attack_object.responce_err_msg[:100])
        else:
            logging.info("Something is not right")


    def handle_attack(self, frow):
        # Handles attack on thread
        # Use it only on threads as .start_request() would block
        # This method can be passed to thread pool executor
        session = self.get_session() # get session for this thread
        attack_object = self.create_attack_object(frow)
        if session != None:
            # offer attack object session before request
            # attack object should use the session during request
            attack_object.set_session(session)
        # start the request(can take some time)
        attack_object.start_request()
        # handles results of the request
        self.handle_attack_results(attack_object, frow)
        # Close responce created from requesnt
        attack_object.close_responce()

    def handle_attacks(self, executor, ftable):
        # Performs attack on provided ftable using threads
        # Useful if attack class not using asyncio
        futures: List[asyncio.Future] = []
        for frow in ftable:
            future = executor.submit(self.handle_attack, frow)
            futures.append(future)
        #concurrent.futures.wait(futures, timeout=self.tasks_wait)
        return futures

    def get_current_tasks(self):
        # Returns currently runningg tasks(fututes)
        return self.current_tasks

    def cancel_current_tasks(self):
        # Cancels current tasks
        for task in self.current_tasks:
            task.cancel()

    def task_done_callback(self, future: Future):
        # Called when task completes
        self.semaphore.release()
        self.current_tasks.discard(future)


    def consumer_done_callback(self):
        # Called when consumer completed
        self.consumer_completed = True

    def producer_done_callback(self):
        # Called when producer completed
        self.producer_completed = True

    def running(self):
        # Returns True when attack is taking place
        return self.consumer_completed or self.producer_completed

    


    def consumer(self):
        # Consumes items in ftable_queue
        # Only maximum of self.total_tasks be used
        with ThreadPoolExecutor(self.total_threads) as executor:
            while True:
                # This will block until one of futures complete
                #print("before self.semaphore.acquire()")
                self.semaphore.acquire()
                #print("after self.semaphore.acquire()")
                try:
                    #print("before self.ftable_queue.get()")
                    # Get frow if available in 0.2 seconds
                    frow = self.ftable_queue.get(timeout=0.2)
                except queue.Empty:
                    # Break the loop if failed to get frow
                    # That may mean producer finished running
                    break
                #print("before executor.submit()")
                future = executor.submit(self.handle_attack, frow)
                # Calls 'self.semaphore.release()' when future completes
                self.current_tasks.add(future)
                #print("before future.add_done_callback()")
                future.add_done_callback(self.task_done_callback)
                #print("after future.add_done_callback()")
        self.close_session()
        self.consumer_done_callback()


    def start(self):
        # setup semaphore and queue at start
        # sets value and maxsize to total_tasks
        self.semaphore = threading.Semaphore(self.total_tasks)
        self.ftable_queue = queue.Queue(self.total_tasks)
        # stores futures from threadpoolexecutor
        futures = []
        with ThreadPoolExecutor(2) as executor:
            futures.append(executor.submit(self.producer))
            futures.append(executor.submit(self.consumer))
            for future in futures:
                # Raises exception if there was error
                future.result()
        
        
class BForceAsync(BForce):
    '''Performs attack on target with data from Ftable object(asyncio)'''
    def __init__(self, target, ftable):
        super().__init__(target, ftable)
        self.current_tasks: Set[asyncio.Task]


    async def close_session(self):
        # Close session object shared by attack objects
        if hasattr(self, "session"):
            attack_class = self.get_attack_class()
            await attack_class.close_session(self.session)

    def get_session(self):
        # Gets session object to be shared with attack objects
        # Realise that thread_local wasnt used
        # Asyncio runs tasks in same thread so session is thread safe
        # We also have choice of when to switch task compared to threads
        if not hasattr(self, "session"):
            self.session = self.create_session()
        # Not thread safe but safe with asyncio
        return self.session

    async def producer_coroutine(self):
        # Creates producer from producer() on different thread
        return await to_thread(self.producer)

    def producer_task(self):
        # Creates async task to producer method
        return asyncio.create_task(self.producer_coroutine)

    async def handle_attack(self, frow):
        #print("run async def handle_attack()")
        # Handles attack on attack class with asyncio support
        session = self.get_session()
        attack_object = self.create_attack_object(frow)
        #print("after self.create_attack_object()")
        if session != None:
            # this line can speed request performance
            attack_object.set_session(session)
        # .start_request() needs to be coroutine method
        await attack_object.start_request()
        self.handle_attack_results(attack_object, frow)
        # Close responce created from request
        await attack_object.close_responce()

    async def handle_attacks(self, ftable):
        # Performs attack on provided ftable using threads
        # Useful if attack class not using asyncio
        tasks:List[asyncio.Task] = []
        for frow in ftable:
            awaitable =  self.handle_attack(frow)
            task = asyncio.ensure_future(awaitable)
            tasks.append(task)
            #task.add_done_callback(background_tasks.discard)
        # asyncio.gather should be future object
        await asyncio.gather(*tasks, return_exceptions=False)


    async def handle_attack_recursive(self, frow):
        await self.handle_attack(frow)
        while True:
            try:
                # Get frow if available in timeout
                frow = self.ftable_queue.get(block=False)
            except queue.Empty:
                # Producer may have finished running
                #print("Breaking from loop, "*2)
                break
            else:
                # Perform attack again on the frow
                #print("statrt handle attack")
                await self.handle_attack(frow)
                #print("handled attack")

    async def handle_attacks_recursive(self, ftable):
        tasks:Set[asyncio.Task] = set()
        for frow in ftable:
            awaitable =  self.handle_attack_recursive(frow)
            task = asyncio.ensure_future(awaitable)
            tasks.add(task)
            self.current_tasks.add(task)
            task.add_done_callback(tasks.discard)
            task.add_done_callback(self.task_done_callback)
        # run tasks asynchronously and wait for completion
        await asyncio.gather(*tasks, return_exceptions=False)


    async def consumer(self):
        # Consumes items in ftable_queue
        # Only maximum of self.total_tasks ftable be used
        frows = self.ftable_queue_elements(self.total_tasks, 0.2)
        if frows:
            # Attacks until all FRows in self.ftable are completed
            # Completion of one task is start of onother
            # until all tasks are completed
            await self.handle_attacks_recursive(frows)
            #print("consumer handle_attacks finished")
        self.consumer_done_callback()
        await self.close_session()


    async def start(self):
        # setup semaphore and queue at start
        # sets value and maxsize to total_tasks
        self.semaphore = threading.Semaphore(self.total_tasks)
        self.ftable_queue = queue.Queue(self.total_tasks)
        # producer and consumer as awaitables
        awaitables = [self.producer_coroutine(), self.consumer()]
        tasks = []
        for awaitable in awaitables:
            task = asyncio.ensure_future(awaitable)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=False)


        

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    # Prepare data for attack
    url = 'https://httpbin.org/post'
    usernames = ["david", "marry", "pearl"] * 1000
    passwords = ["1234", "0000", "th234"]

    # Creates columns for table
    usernames_col = FColumn('usernames', usernames)
    # Sets key name to use in row key in Table
    usernames_col.set_item_name("username")
    passwords_col = FColumn('passwords', passwords)
    passwords_col.set_item_name("password")

    table = FTable()
    # Set common row to be shared by all rows
    common_row = FRow()
    common_row.add_item("submit", "login")
    table.set_common_row(common_row)
    # Add columns to table
    table.add_column(usernames_col)
    table.add_column(passwords_col)



    
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

