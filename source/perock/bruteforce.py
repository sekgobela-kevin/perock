'''
Performs attack with multiple attempts
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''

import inspect
from typing import List, Type
import logging
import queue
import threading
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
#from concurrent.futures import as_completed
#import concurrent.futures


from .attack import Attack
from .attack import AttackAsync
from .attack import WebAttackAsync
from .attack import WebAttack

from .forcetable import FColumn
from .forcetable import FRow
from .forcetable import FTable

# asyncio.to_thread() is New in Python version 3.9.
# see https://docs.python.org/3/library/asyncio-task.html#id10
from .util import to_thread


class BForce():
    '''Performs attack on target with data from FTable object(threaded)'''
    def __init__(self, target, ftable) -> None:
        self.target = target
        self.ftable = ftable

        # Total independed tasks to run
        # Corresponds to requests that will be executed concurrently
        self.total_tasks = 500
        # Threads to use on self.total_tasks
        self.total_threads = 50 # 30 threads
        # Time to wait to complete self.total_tasks
        self.tasks_wait = 100 

        # store thread specific attributes
        # e.g session object
        self.thread_local = threading.local()

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

    def get_attack_class(self) -> Attack:
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

    def create_attack_object(self, data) -> Type[Attack]:
        # Creates attack object with set attack class
        # .get_attack_class() will raise error if not found
        attack_class = self.get_attack_class()
        return attack_class(self.target, data)

    def producer(self):
        # Added ftable to ftable queue
        for frow in self.ftable:
            # queue.put() will block if queue is already full
            print("producer put")
            self.ftable_queue.put(frow)


    def ftable_queue_elements(self, size=None, timeout=0.2):
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
                # That may mean produser finished running
                break
            else:
                ftable.append(frow)  
            count += 1
        # If ftable is empty, ftable_queue may be empty
        # Produser may have stopped or timeout is too small
        return ftable



    def handle_attack_results(self, attack_object:Type[Attack]):
        # Handles results of attack on attack object
        # start_request() was already called and finished
        # responce can be accessed with self.responce
        if not attack_object.errors():
            logging.info("Attack sucessful: " + str(attack_object.data))
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
        self.handle_attack_results(attack_object)
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


    def done_callback(self, future):
        self.semaphore.release()
        #future.result()


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
                    print("before self.ftable_queue.get()")
                    # Get frow if available in 0.2 seconds
                    frow = self.ftable_queue.get(timeout=0.2)
                except queue.Empty:
                    # Break the loop if failed to get frow
                    # That may mean produser finished running
                    break
                #print("before executor.submit()")
                future = executor.submit(self.handle_attack, frow)
                # Calls 'self.semaphore.release()' when future completes
                #print("before future.add_done_callback()")
                future.add_done_callback(self.done_callback)
                #print("after future.add_done_callback()")
            self.close_session()


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
        #self.total_tasks = 8000


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
        # Creates async task to produser method
        return asyncio.create_task(self.producer_coroutine)

    async def handle_attack(self, frow):
        print("run async def handle_attack()")
        # Handles attack on attack class with asyncio support
        session = self.get_session()
        attack_object = self.create_attack_object(frow)
        print("after self.create_attack_object()")
        if session != None:
            # this line can speed request performance
            attack_object.set_session(session)
        # .start_request() needs to be coroutine method
        await attack_object.start_request()
        self.handle_attack_results(attack_object)
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


    async def consumer(self):
        # Consumes items in ftable_queue
        # Only maximum of self.total_tasks ftable be used
        while True:
            ftable = self.ftable_queue_elements(
                self.total_tasks, 0.2)
            print("consumer ftable", ftable)
            if not ftable:
                # ftable cant be empty
                # produser may have finished
                break
            print("consumer waiting for self.handle_attacks")
            await self.handle_attacks(ftable)
            print("consumer handle_attacks finished")
        # Closes session object
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

