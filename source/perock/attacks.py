'''
Contains ready to use attack classes

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from .attack import Attack
from .attack import AttackAsync

import asyncio
import importlib
import time


class _WebAttackMixin():
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
            self.responce_msg = self.responce.reason

    def responce_status_code(self, responce):
        # Access status code from responce
        raise NotImplementedError

    @property
    def status_code(self):
        return self.responce_status_code(self.responce)

    @property
    def text(self):
        if self.target_reached():
            return self.responce.text

    @property
    def content(self):
        if self.target_reached():
            return self.responce.content

    def target_errors(self):
        if self.target_reached():
            status_code = self.status_code
            return status_code >= 500 and status_code < 600
        return super().target_errors()

    def client_errors(self):
        if self.target_reached():
            status_code = self.status_code
            return status_code >= 400 and status_code < 500
        return super().client_errors()


class WebAttack(_WebAttackMixin, Attack):
    '''Attempts to log into website with provided data'''
    def __init__(self, target, data: dict, retries=1) -> None:
        # _WebAttackMixin.__init__() and Attack.__init__()
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
        if self.target_reached():
            return self.responce.text()

    @property
    def content(self):
        if self.target_reached():
            return self.responce.content()


class WebAttackAsync(_WebAttackMixin, AttackAsync):
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
    async def create_session(cls):
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
        if self.target_reached():
            return await self.responce.text()

    @property
    async def content(self):
        if self.target_reached():
            return await self.responce.content()



class _TestAttackMatrix():
    '''Attack class for testing purposes'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep_time = 4


    def set_sleep_time(self, seconds):
        self.sleep_time = seconds

    def create_fake_responce(self):
        # Creates fake responce object from target
        class Responce():
            elapsed_time = self.sleep_time
            request_data = self.data
            status = 200
            text = "This is responce text from target"
        return Responce()



class TestAttack(_TestAttackMatrix, Attack):
    '''Attack class for testing purposes'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, 1)

    def request(self):
        time.sleep(self.sleep_time)
        return self.create_fake_responce()

    
class TestAttackAsync(_TestAttackMatrix, AttackAsync):
    '''Asynchronous Attack class for testing purposes'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, 1)

    async def request(self):
        await asyncio.sleep(self.sleep_time)
        return self.create_fake_responce()



if __name__ == "__main__":
    url = 'https://httpbin.org/post'
    data = {'key1': 'value1', 'key2': 'value2'}
    test_obj = WebAttackAsync(url, data)
    

    asyncio.run(test_obj.start_request())
    print("test_obj.request_error", test_obj.request_error())
    print("test_obj.errors()", test_obj.errors())
    print("test_obj.target_reached", test_obj.target_reached())
    print("test_obj.errors()", test_obj.errors())
    print("test_obj.text", asyncio.run(test_obj.text))

