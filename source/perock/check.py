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
        return self._attempt_object.request_failed

    def errors(self):
        '''Returns True if there errors(target or client)'''
        # Returns True if there errors
        # Error can be on client(our code) or the target(e.g webserver)
        return self.target_errors() or self.client_errors()

    def responce_errors(self):
        '''Returns True if responce from target has errors'''
        return None

