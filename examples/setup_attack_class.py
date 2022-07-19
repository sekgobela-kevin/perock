import requests

from perock import attack


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
            return b"Failed to login" in self._responce.content
        # Since target was not reached, there was never failure
        return False


if __name__ == "__main__":
    # Now go to webapp folder and run 'main.py'
    # cd examples
    # python webapp/main.py

    # "http://127.0.0.1:5000" thats urls it was running on.
    # Replace it if different on your machine.
    request_data = {"username": "ANDERSON", "password": "shuttle"}
    web_attack = WebAttack("http://127.0.0.1:5000/login", request_data)
    web_attack.start()

    # If webapp is running
    # --------------------

    print(web_attack.target_reached()) # True
    print(web_attack.client_errors()) # False
    print(web_attack.target_errors()) # False
    
    print("")
    # One of them needs to be True
    print(web_attack.errors()) # False
    print(web_attack.failure()) # False
    print(web_attack.success()) # True

    print(web_attack.get_responce().status_code) # 200



    # If webapp is running
    # --------------------
    print("\n"*2)

    print(web_attack.target_reached()) # False
    print(web_attack.client_errors()) # True
    print(web_attack.target_errors()) # False
    
    print("")
    # One of them needs to be True
    print(web_attack.errors()) # True
    print(web_attack.failure()) # False
    print(web_attack.success()) # False

    print(isinstance(web_attack.get_responce(), Exception)) # True




