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

    def after_request(self):
        super().after_request()
        if self.success():
            print("Attempt success:", self._data)
        elif self.errors():
            print("Attempt errors:", self._data)
            print("Responce message:", self._responce_msg)



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

    async def after_request(self):
        await super().after_request()
        if await self.success():
            print("Attempt success:", self._data)
        elif await self.errors():
            print("Attempt errors:", self._data)
            print("Responce message:", self._responce_msg)



