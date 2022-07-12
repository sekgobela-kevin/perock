'''Responsible for communicating with target or system.
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''

from typing import List, Set


def try_close(object):
    # Attempts to close provided object
    try:
        # This should work in most cases
        object.close()
    except (AttributeError):
        # object cannot be closed
        pass

async def try_close_async(object):
    # Attempts to close provided object asynchonously
    try:
        # This should work in most cases
        await object.close()
    except (AttributeError, TypeError):
        # object cannot be closed
        pass


class Attempt():
    '''
    Attempts to log into system with data. System can be
    anything that requires certain credentials to access.
    This can include website or file requiring username and
    password to access.'''
    unraised_exceptions_classes: Set[BaseException] = set()

    def __init__(self, target, data:dict, retries=1) -> None:
        '''
        target - system to send data to e.g url
        data - data to send to target'''
        self.target = target
        self.data = data

        # session to share with other attack object
        self.session = None
        # Error message from responce
        self.responce_msg = None
        # represents our responce
        self.responce = None

    def get_responce_message(self):
        return self.responce_msg

    def get_target(self):
        # Returns target to be used for attack
        return self.target

    def get_data(self):
        # Returns data to be used for attack
        return self.data

    @classmethod
    def add_unraised_exception(cls, exception):
        # Adds exception not to be raised on .request(self)
        cls.unraised_exceptions_classes.add(exception)

    def remove_unraised_exception(cls, exception):
        # Removes exception not to be raised on .request(self)
        cls.unraised_exceptions_classes.discard(exception)

    @classmethod
    def _should_raise_exception(cls, exception):
        # Returns True if exception should be raised on .request(self)
        if isinstance(exception, BaseException):
            for unraised_exception in cls.unraised_exceptions_classes:
                if isinstance(exception, unraised_exception):
                    return False
            return True
        else:
            err_msg = "exception needs to be BaseException not" +\
            " " + str(type(exception))
            raise TypeError(err_msg)

    def validate_data(self, data):
        '''Checks if data is in valid for request'''
        # if not isinstance(data, dict):
        #     #err_msg = "data needs to be in dictionary form"
        #     #raise TypeError(err_msg)
        #     return False
        return True

    @classmethod
    def create_session(cls):
        # Creates session object to use with request
        raise NotImplementedError
       

    def close_session(self):
        '''Closes session object'''
        try_close(self.session)
        assert self.session.closed

    def close_responce(self):
        "Closes responce object"
        try_close(self.responce)
        

    def set_session(self, session):
        '''Sets session object structure to use with .request().
        session can be anything that be reused with request.'''
        self.session = session

    def get_session(self):
        try:
            return self.session
        except AttributeError:
            return None
            #err_msg = "session object not found"
            #err_msg2 = "please set session with .set_session()"
            #raise AttributeError(err_msg, err_msg2)
            pass

    def get_responce(self):
        '''Returns responce from target'''
        return self.responce
        

    def request(self):
        "Sends data to target to be tested, returns responce"
        # use our target and data to return responce
        # None or False should be returned if it fails
        # Also set fail_msg if error is encountered or it fails
        err_msg = "request() method not implemented"
        raise NotImplementedError(err_msg)

    def before_start_request(self):
        # Called im,edeiately when start_request() is called
        if not self.validate_data(self.data):
            err_msg = f"Data({self.data}) is not valid"
            err_msg2 = "check if the data is in right format"
            raise ValueError(err_msg, err_msg2)

    def after_start_request(self):
        # Called after start_request() completes
        pass


    def request_error(self):
        '''Checks if request failed(exception was raised)'''
        # Returns True if request failed
        # request_error() is to simple
        # Subclasses can implement it further
        return isinstance(self.responce, Exception)

    def start_request(self, retries=1):
        '''Start a request and update internal attributes based on
        returned responce'''
        self.before_start_request()
        try:
            self.responce =  self.request()
        except Exception as e:
            if self._should_raise_exception(e):
                raise e
            else:
                self.responce = e
                self.responce_msg = str(e)
        if self.responce == None:
            err_msg = "responce cant be None"
            raise Exception(err_msg)
        self.after_start_request()
        

    def target_reached(self):
        '''Checks if target was reached. Target was reached
        if target was able to receive request and return responce.'''
        # Checks if target was reached
        # This means the target responded
        if self.responce == None:
            return False
        return not self.request_error()

    def close(self):
        #self.close_session()
        if self.responce:
            self.close_responce()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()




class AttemptAsync(Attempt):
    '''Asyncio version of Attempt class'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)

    @classmethod
    async def create_session(cls):
        # Creates session object to use with request
        raise NotImplementedError

    async def close_session(self):
        '''Closes session object'''
        await try_close_async(self.session)

    async def close_responce(self):
        "Closes responce object"
        await try_close_async(self.responce)

    async def before_start_request(self):
        super().before_start_request()

    async def after_start_request(self):
        super().after_start_request()

    async def request(self):
        # Strictly should be async with await
        # Responce should be returned else None if request failed
        err_msg = "request() method not implemented"
        raise NotImplementedError(err_msg)

    async def start_request(self, retries=1):
        '''Start a request and update internal attributes based on
        returned responce'''
        await self.before_start_request()
        try:
            self.responce =  await self.request()
        except Exception as e:
            if self._should_raise_exception(e):
                raise e
            else:
                self.responce = e
                self.responce_msg = str(e)
        if self.responce == None:
            err_msg = "responce cant be None"
            raise Exception(err_msg)
        await self.after_start_request()

    async def close(self):
        #self.close_session()
        if self.responce:
            await self.close_responce()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    


if __name__ == "__main__":
    import requests

    class WebLogAttempt(Attempt):
        def __init__(self, target, data: dict, retries=1) -> None:
            super().__init__(target, data, retries)
            self.request: requests.Request

        def request(self):
            return requests.post(self.target, params=self.data)

        @property
        def text(self):
            if self.target_reached:
                return self.responce.text


    url = 'https://httpbin.org/get'
    data = {'key1': 'value1', 'key2': 'value2'}
    attempt_obj = WebLogAttempt(url, data)
    attempt_obj.start_request()
    print(attempt_obj.request_error)
    print(attempt_obj.request_error_msg)
    print(type(attempt_obj.text))

