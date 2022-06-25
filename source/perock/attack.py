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

