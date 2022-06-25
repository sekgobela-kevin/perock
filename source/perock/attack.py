'''
Communicates with target/system and also analyse responce on 
single attempt.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from .attempt import Attempt
from .attempt import AttemptAsync
from .check import Check

import asyncio
import importlib


class Attack(Attempt, Check):
    '''Attempts to logs into system with data'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # Multiple inheritance is causing problems
        # Hope __init__(self, self) wont cause problems
        # Note that Check class composites Attempt class
        # As 'self' is subclass(derived) of Attempt
        # It can be passed in place of Attempt object
        # I hope this does not add performance overhead(but it works)
        Check.__init__(self, self)

    def responce_errors(self):
        '''Returns True if responce from target has errors'''
        if self.target_reached:
            return self.errors()
        return super().responce_errors()


class AttackAsync(AttemptAsync, Check):
    '''Perform attack using request implemeted with asyncio'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        Check.__init__(self, self)




class WebAttackMixin():
    '''Attempts to log into website with provided data.'''
    # What are mixins?
    # see here: https://stackoverflow.com/questions/9575409/
    # calling-parent-class-init-with-multiple-
    # inheritance-whats-the-right-way
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def after_request(self):
        # Method is excuted after request completes
        if self.responce_errors():
            self.responce_err_msg = self.responce.reason

    def responce_status_code(self, responce):
        # Access status code from responce
        raise NotImplementedError

    @property
    def status_code(self):
        return self.responce_status_code(self.responce)

    @property
    def text(self):
        if self.target_reached:
            return self.responce.text

    @property
    def content(self):
        if self.target_reached:
            return self.responce.content

    def target_errors(self):
        if self.target_reached:
            status_code = self.status_code
            return status_code >= 500 and status_code < 600
        return super().target_errors()

    def client_errors(self):
        if self.target_reached:
            status_code = self.status_code
            return status_code >= 400 and status_code < 500
        return super().client_errors()


class WebAttack(WebAttackMixin, Attack):
    '''Attempts to log into website with provided data'''
    def __init__(self, target, data: dict, retries=1) -> None:
        # WebAttackMixin.__init__() and Attack.__init__()
        # should be called
        super().__init__(target, data, retries)
        # dynmically import requests module
        self.requests = importlib.import_module("requests")
        self.request: self.requests.Request
        self.responce: self.requests.Response

    @classmethod
    def create_session(cls):
        # Creates session object to use with request
        requests = importlib.import_module("requests")
        return requests.Session()

    def request(self):
        session = self.get_session()
        if session == None:
            # session object wasnt provided
            # we then perform request direcly
            return self.requests.post(self.target, data=self.data)
        else:
            # session would improve request performance
            return session.post(self.target, data=self.data)


    def responce_status_code(self, responce):
        # Access status code from responce
        return responce.status_code

    @property
    def text(self):
        if self.target_reached:
            return self.responce.text()

    @property
    def content(self):
        if self.target_reached:
            return self.responce.content()


class WebAttackAsync(WebAttackMixin, AttackAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # Dynamically import aiohttp
        self.aiohttp = importlib.import_module("aiohttp")
        self.request: self.aiohttp.ClientRequest
        self.responce: self.aiohttp.ClientResponse

    def responce_status_code(self, responce):
        # Access status code from responce
        return responce.status

    @classmethod
    def create_session(cls):
        # Creates session object to use with request
        aiohttp = importlib.import_module("aiohttp")
        return aiohttp.ClientSession()

    async def request(self):
        session = self.get_session()
        if session == None:
            # Creates session and perform request
            # Session is closed but responce is not
            async with self.create_session() as session:
                return await session.post(self.target, data=self.data)
        else:
            # Use existing session to improve performance
            # No need to close session as its reused(DONT)
            return await session.post(self.target, data=self.data)
                

    @property
    async def text(self):
        if self.target_reached:
            return await self.responce.text()

    @property
    async def content(self):
        if self.target_reached:
            return await self.responce.content()



if __name__ == "__main__":
    url = 'https://httpbin.org/post'
    data = {'key1': 'value1', 'key2': 'value2'}
    test_obj = WebAttackAsync(url, data)
    

    asyncio.run(test_obj.start_request())
    print("test_obj.request_failed", test_obj.request_failed)
    print("test_obj.request_fail_msg", test_obj.request_fail_msg)
    print("test_obj.errors()", test_obj.errors())
    print("test_obj.target_reached", test_obj.target_reached)
    print("test_obj.errors()", test_obj.errors())
    #print("test_obj.responce()", test_obj.responce)
    print("test_obj.text", asyncio.run(test_obj.text))
    print("test_obj.responce_err_msg", test_obj.responce_err_msg)

