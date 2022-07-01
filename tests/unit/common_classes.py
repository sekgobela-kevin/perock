
class Request():
    def __init__(self, data) -> None:
        self.data = data
        self.closed = False

    def close(self):
        self.closed = True


class Responce():
    def __init__(self) -> None:
        self.target_error_msg = "Target has experienced errors"
        self.client_error_msg = "Something is wrong with client request"
        self.denied_error_msg = "Access to target was denied"
        self.success_message = "Logged in to system"
        self.fail_message = "Provided credentials are not valid"

        self.target_error = False
        self.client_error = False
        self.denied_error = False
        self.failed = False
        self.success = True

        self.closed = False
    
    def close(self):
        self.closed = True

    def message(self):
        if self.denied_error:
            return self.denied_error_msg
        elif self.client_error:
            return self.client_error_msg
        elif self.target_error:
            return self.target_error_msg
        elif self.success:
            return self.success_message
        else:
            return self.fail_message


class Session():
    def __init__(self, data={}) -> None:
        self.data = data
        self.closed = False

    def add_item(self, key, val):
        self.data[key] = val

    def get_item(self, key):
        return self.data[key]

    def close(self):
        self.closed = True
    
