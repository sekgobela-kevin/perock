'''Responsible for communicating with target or system.
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''

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

error_responce = object()

class Attempt():
    '''
    Attempts to log into system with data. System can be
    anything that requires certain credentials to access.
    This can include website or file requiring username and
    password to access.'''
    '''Checks if provided data is valid for system'''
    def __init__(self, target, data:dict, retries=1) -> None:
        '''
        target - system to send data to e.g url
        data - data to send to target'''
        self.target = target
        self.data = data

        self.request_exception = None
        self.request_error_msg = None
        # output of request() when it failed
        self.error_responce = object()

        # represents our responce
        self.responce = None
        self.responce_error_msg = None

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
       

    @classmethod
    def close_session(cls, session):
        '''Closes session object'''
        try_close(session)

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
        if self.target_reached():
            return self.responce
        return None
        

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
        return self.responce == self.error_responce

    def start_request(self, retries=1):
        '''Start a request and update internal attributes based on
        returned responce'''
        self.before_start_request()
        self.responce =  self.request()
        self.after_start_request()
        

    def target_reached(self):
        '''Checks if target was reached. Target was reached
        if target was able to receive request and return responce.'''
        # Checks if target was reached
        # This means the target responded
        if self.responce == None:
            return False
        return not self.request_error()



class AttemptAsync(Attempt):
    '''Asyncio version of Attempt class'''
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)


    @classmethod
    async def close_session(cls, session):
        '''Closes session object'''
        await try_close_async(session)

    async def close_responce(self):
        "Closes responce object"
        await try_close_async(self.responce)

    async def request(self):
        # Strictly should be async with await
        # Responce should be returned else None if request failed
        err_msg = "request() method not implemented"
        raise NotImplementedError(err_msg)

    async def start_request(self, retries=1):
        '''Start a request and update internal attributes based on
        returned responce'''
        self.before_start_request()
        for _ in range(retries):
            try:
                self.responce =  await self.request()
            except Exception as e:
                self.responce = self.error_responce
                self.request_error_msg = str(e)
            if not self.request_error:
                break
        self.after_start_request()


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

