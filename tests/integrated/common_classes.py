from perock import attack
from perock.target import *



class AttackSample(attack.Attack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self._target: Target
        self.account = Account(self._data)

    def request(self):
        # Returns Fake responce
        return self._target.login(self.account)

    def success(self):
        return self._target.account_success(self.account)




class AttackAsyncSample(attack.AttackAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        self._target: Target
        self.account = Account(self._data)

    async def request(self):
        # Returns Fake responce
        return self._target.login(self.account)

    async def success(self):
        return self._target.account_success(self.account)



