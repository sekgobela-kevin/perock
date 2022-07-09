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

    def get_attempt_object(self):
        '''Returns Attempt class instance. Attempt object
        is the one with responce from attempting to log to target'''
        return self._attempt_object

    def success(self):
        '''Returns True if data works for the system,
        that means attack was successful'''
        # Return True if attempt was successful
        # That means data works and is valid for the system
        raise NotImplementedError

    def failure(self):
        # Returns True if attempt to log to system failed
        # It may be False because of errors or target not reached
        return not self.success()

    def target_errors(self):
        '''Checks if there were error at target side'''
        # Checks if there were error on target side
        # There may be errors on target e.g 'server errors'
        #raise NotImplementedError
        return None

    def client_errors(self):
        '''Returns True if there were errors on client(our side)'''
        # Returns True if there were errors on client
        # This means request failed to even start
        # e.g 'Invalid url' or 'no internet connection'
        return self._attempt_object.request_error()

    def errors(self):
        '''Returns True if there errors(target or client)'''
        # Returns True if there errors
        # Error can be on client(our code) or the target(e.g webserver)
        return  self.client_errors() or self.target_errors()

    def responce_errors(self):
        '''Returns True if responce from target has errors'''
        if self._attempt_object.target_reached():
            return self.errors()
        return None


class CheckAsync(Check):
    def __init__(self, attempt_object) -> None:
        super().__init__(attempt_object)

    async def success(self):
        return super().success()

    async def failure(self):
        return not await self.success()

    async def target_errors(self):
        return super().target_errors()

    async def client_errors(self):
        return super().client_errors()

    async def errors(self):
        return  await self.client_errors() or await self.target_errors()

    async def responce_errors(self):
        if self._attempt_object.target_reached():
            return await self.errors()
        return None