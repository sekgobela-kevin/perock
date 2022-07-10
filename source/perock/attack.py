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
from .check import CheckAsync

from .responce import BytesCompare


class Attack(Attempt, Check):
    '''Attempts to logs into system with data'''
    base_attempt_class = Attempt
    base_check_class = Check

    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # Multiple inheritance is causing problems
        # Hope __init__(self, self) wont cause problems
        # Note that Check class composites Attempt class
        # As 'self' is subclass(derived) of Attempt
        # It can be passed in place of Attempt object
        # I hope this does not add performance overhead(but it works)
        self.base_check_class.__init__(self, self)

    def after_start_request(self):
        # Called after start_request() completes
        super().after_start_request()
        if self.responce_errors():
            # The error messages are not detailed
            # Subclasses will have to define detailed ones
            main_err_msg = "Target experienced errors"
            if self.target_errors():
                self.responce_msg = f"{main_err_msg}(fault 'Target')"
            elif self.client_errors():
                self.responce_msg = f"{main_err_msg}(fault 'Client')"


class AttackText(Attack, BytesCompare):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        BytesCompare.__init__(self, b"")
        super().__init__(target, data, retries)

    def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    def success(self) -> bool:
        return BytesCompare.success(self)

    def failure(self) -> bool:
        return BytesCompare.failure(self)

    def target_errors(self) -> bool:
        return BytesCompare.target_error(self)

    def client_errors(self) -> bool:
        if super().client_errors():
            return True
        return BytesCompare.target_error(self)

    def after_start_request(self):
        super().after_start_request()
        responce_content = self.responce_content()
        responce_bytes = self._create_responce_bytes(responce_content)
        self._responce_bytes = responce_bytes



class AttackAsync(AttemptAsync, CheckAsync):
    '''Perform attack using request implemeted with asyncio'''
    base_attempt_class = AttemptAsync
    base_check_class = CheckAsync

    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self.base_check_class.__init__(self, self)

    async def after_start_request(self):
        # Called after start_request() completes
        await super().after_start_request()
        if await self.responce_errors():
            # The error messages are not detailed
            # Subclasses will have to define detailed ones
            main_err_msg = "Target experienced errors"
            if await self.target_errors():
                self.responce_msg = f"{main_err_msg}(fault 'Target')"
            elif await self.client_errors():
                self.responce_msg = f"{main_err_msg}(fault 'Client')"



class AttackTextAsync(AttackAsync, BytesCompare):
    '''Attack class with responce containing bytes or text'''
    def __init__(self, target, data: dict, retries=1) -> None:
        BytesCompare.__init__(self, b"")
        super().__init__(target, data, retries)

    async def responce_content(self) -> str:
        '''Returns string or bytes from responce'''
        raise NotImplementedError

    async def success(self) -> bool:
        return BytesCompare.success(self)

    async def failure(self) -> bool:
        return BytesCompare.failure(self)

    async def target_errors(self) -> bool:
        return BytesCompare.target_error(self)

    async def client_errors(self) -> bool:
        if await super().client_errors():
            return True
        return BytesCompare.target_error(self)

    async def after_start_request(self):
        await super().after_start_request()
        responce_content = await self.responce_content()
        responce_bytes = self._create_responce_bytes(responce_content)
        self._responce_bytes = responce_bytes


