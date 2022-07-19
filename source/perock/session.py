'''
Module with classes containing methods for session to be used 
by BForce classes.

Author: Sekgobela Kevin
Date: July 2022
Languages: Python 3
'''
import threading

class BForceSession():
    def __init__(self) -> None:
        self._thread_local = threading.local()

    def create_session(self):
        # Creates session object to be shared with attack objects
        raise NotImplementedError

    def close_session(self):
        # Creates session object
        raise NotImplementedError

    def session_exists(self):
        # Returns True if session exists
        return hasattr(self._thread_local, "session")

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._thread_local.session = session

    def get_session(self):
        # Gets session object to be shared with attack objects
        if not self.session_exists():
            # This is thread safe
            return self._thread_local.session
        return None

    def create_get_session(self):
        # Gets session if exists else creates one
        if self.session_exists():
            return self.get_session()
        else:
            try:
                return self.create_session()
            except NotImplementedError:
                return None



class BForceBlockSession(BForceSession):
    def __init__(self) -> None:
        super().__init__()
        self._session = None

    def session_exists(self):
        # Returns True if session object exists
        return self._session != None

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self._session = session

    def get_session(self):
        if not self.session_exists():
            # Not thread safe but safe with asyncio
            return self._session
        return None

    def create_get_session(self):
        # Gets session if exists else creates one
        if self.session_exists():
            return self.get_session()
        else:
            try:
                return  self.create_session()
            except NotImplementedError:
                return None



class BForceAsyncSession(BForceBlockSession):
    def __init__(self) -> None:
        super().__init__()

    async def create_session(self):
        raise NotImplementedError

    def get_session(self):
        # Gets session object to be shared with attack objects
        # Realise that thread_local wasnt used
        # Asyncio runs tasks in same thread so session is thread safe
        # We also have choice of when to switch task compared to threads
        if not self.session_exists():
            # Not thread safe but safe with asyncio
            return self._session
        return None

    async def create_get_session(self):
        # Gets session if exists else creates one
        if self.session_exists():
            return self.get_session()
        else:
            try:
                return await self.create_session()
            except NotImplementedError:
                return None
