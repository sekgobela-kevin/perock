'''
Analyses responce or output of attempt to check if access was granted
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from .attempt import Attempt


class Check():
    '''Checks and analyses responce from attempt to log to system
    with given data.'''
    def __init__(self, attempt_object) -> None:
        self._attempt_object:Attempt = attempt_object
        #self._responce = self._attempt_object.get_responce()

    def get_attempt_object(self):
        '''Returns Attempt class instance. Attempt object
        is the one with responce from attempting to log to target'''
        return self._attempt_object

    def request_started(self) -> bool:
        '''Returns True if request was ever started'''
        responce = self._attempt_object.get_responce()
        return responce != None


    def request_failed(self):
        '''Returns True if request failed(likely bacause of exception)'''
        responce = self._attempt_object.get_responce()
        return isinstance(responce, Exception)


    def target_reached(self):
        '''Checks if target was reached. Target was reached
        if target was able to receive request and return responce.'''
        if not self.request_started():
            return False
        elif self.request_failed():
            return False
        else:
            return True

    def success(self):
        '''Returns True if data works for the system,
        that means attack was successful'''
        # Return True if attempt was successful
        # That means data works and is valid for the system
        raise NotImplementedError

    def failure(self):
        '''Returns True if attempt to log to system failed'''
        # This method should raise not implemented error.
        # Developer should implement this method.
        # But we can guess if there was failure based on success.
        if self.target_reached():
            # If theres is no error or sucess then it may be failure.
            # This should work in most cases.
            return not (self.success() or self.errors())
        # Failure is not expected if target was reached.
        return False

    def target_errors(self):
        '''Checks if there were error at target side'''
        # Checks if there were error on target side
        # There may be errors on target e.g 'server errors'
        #raise NotImplementedError
        return False

    def client_errors(self):
        '''Returns True if there were errors on client(our side)'''
        # Returns True if there were errors on client
        # This means request failed to even start
        # e.g 'Invalid url' or 'no internet connection'
        return self.request_failed()

    def errors(self):
        '''Returns True if there errors(target or client)'''
        # Returns True if there errors
        # Error can be on client(our code) or the target(e.g webserver)
        return  self.client_errors() or self.target_errors()

    def responce_errors(self):
        '''Returns True if responce from target has errors'''
        if self.target_reached():
            return self.errors()
        return False


class CheckAsync(Check):
    def __init__(self, attempt_object) -> None:
        super().__init__(attempt_object)

    async def target_reached(self):
        return super().target_reached()
    
    async def success(self):
        return super().success()

    async def failure(self):
        # This method guesses failure based on sucess and error.
        # Its reccommended to implement this method.
        # But it should work well in most/all cases.
        if await self.target_reached():
            # If theres is no error or sucess then it may be failure.
            return not (await self.success() or await self.errors())
        return False

    async def target_errors(self):
        return super().target_errors()

    async def client_errors(self):
        return super().client_errors()

    async def errors(self):
        return  await self.client_errors() or await self.target_errors()

    async def responce_errors(self):
        '''Returns True if responce from target has errors'''
        if await self.target_reached():
            return await self.errors()
        return False
