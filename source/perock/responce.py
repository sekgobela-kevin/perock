


class ResponceBytes():
    '''Represents bytes from responce'''
    def __init__(self, __bytes=b""):
        if isinstance(__bytes, ResponceBytes):
            self._bytes = __bytes.get_bytes()
        else:
            self._bytes = self.to_bytes(__bytes)
        self._contains_strict = True

    def get_bytes(self):
        return self._bytes

    def enable_contains_strict(self):
        self._contains_strict = True

    def disable_contains_strict(self):
        self._contains_strict = False

    @classmethod
    def to_bytes(cls, text):
        if isinstance(text, bytes):
            return text
        elif isinstance(text, str):
            return text.encode()
        else:
            err_msg = f"Text should be string or bytes not {type(text)}"
            raise TypeError(err_msg)

    @classmethod
    def to_text(cls, text):
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode()
        else:
            err_msg = f"Text should be string or bytes not {type(text)}"
            raise TypeError(err_msg) 

    @classmethod
    def contains_filter(cls, _bytes, bytes_iterator):
        def func(bytes):
            return cls.to_bytes(bytes) in _bytes
        return filter(func, bytes_iterator)

    def contains_any(self, bytes_iterator):
        filtered = list(self.contains_filter(self._bytes, bytes_iterator))
        return bool(filtered)

    def contains_all(self, bytes_iterator):
        filtered = list(self.contains_filter(self._bytes, bytes_iterator))
        if not filtered:
            return False
        return len(filtered) == len(bytes_iterator)

    def contains_iterator(self, bytes_iterator):
        if self._contains_strict:
            return self.contains_all(bytes_iterator)
        else:
            return self.contains_any(bytes_iterator)

    def lower(self):
        return self.__class__(self._bytes.lower())

    def upper(self):
        return self.__class__(self._bytes.upper())


    def __eq__(self, __o: object) -> bool:
        return self._bytes == __o.get_bytes()

    def __str__(self) -> str:
        return self.to_text(self._bytes)

    def __add__(self, other):
        return self.__class__(self.get_bytes() + other.get_bytes())

    def __contains__(self, other):
        #if isinstance(other, self.__class__):
        #    return other.to_bytes() in self._bytes
        if isinstance(other, (str, bytes)):
            return self.to_bytes(other) in self._bytes
        else:
            return self.contains_iterator(other)

    def __len__(self):
        return len(self._bytes)

    def __iter__(self):
        return iter(self._bytes)



class ResponceAnalyserBase():
    '''Compares responce with other objects'''
    def __init__(self, responce, other) -> None:
        self._responce = responce
        self._other = other

    def target_reached(self):
        raise NotImplementedError

    def success(self):
        raise NotImplementedError

    def failure(self):
        raise NotImplementedError

    def error(self):
        raise NotImplementedError

    def wait_error(self):
        raise NotImplementedError

    def not_found_error(self):
        raise NotImplementedError

    def access_denied_error(self, account):
        raise NotImplementedError

    def target_error(self, account):
        raise NotImplementedError

    def client_error(self, account):
        raise NotImplementedError


class ResponceBytesAnalyser(ResponceAnalyserBase):
    '''Compares bytes of responce with other bytes'''
    def __init__(self, bytes_string, contains_strict=False) -> None:
        super().__init__(bytes_string, None)
        self._bytes_string = bytes_string
        self._contains_strict = contains_strict

        self._target_reached_bytes_strings = set()

        self._success_bytes_strings = set()
        self._failure_bytes_strings = set()
        self._error_bytes_strings = set()

        self._wait_error_bytes_strings = set()
        self._not_found_error_bytes_strings = set()
        self._access_denied_error_bytes_strings = set()

        self._target_error_bytes_strings = set()
        self._client_error_bytes_strings = set()
        self._error_bytes_strings = set()

        # Updates and setup self._responce_bytes
        self.update()

    def enable_contains_strict(self):
        self._responce_bytes.enable_contains_strict()

    def disable_contains_strict(self):
        self._responce_bytes.disable_contains_strict()

    def _create_responce_bytes(self):
        responce_bytes = ResponceBytes(self._bytes_string)
        if self._contains_strict:
            responce_bytes.enable_contains_strict()
        else:
            responce_bytes.disable_contains_strict()
        return responce_bytes

    def update(self, bytes_string: bytes=None):
        # Updates self._responce_bytes to match with bytes_string
        if bytes_string != None:
            self._bytes_string = bytes_string
        self._responce_bytes = self._create_responce_bytes()

    def set_target_reached_bytes_strings(self, bytes_strings):
        self._target_reached_bytes_strings = set(bytes_strings)

    def set_success_bytes_strings(self, bytes_strings):
        self._success_bytes_strings = set(bytes_strings)

    def set_failure_bytes_strings(self, bytes_strings):
        self._failure_bytes_strings = set(bytes_strings)

    def set_error_bytes_strings(self, bytes_strings):
        self._error_bytes_strings = set(bytes_strings)


    def set_wait_error_bytes_strings(self, bytes_strings):
        self._wait_error_bytes_strings = set(bytes_strings)

    def set_not_found_error_bytes_strings(self, bytes_strings):
        self._not_found_error_bytes_strings = set(bytes_strings)

    def set_access_denied_error_bytes_strings(self, bytes_strings):
        self._access_denied_error_bytes_strings = set(bytes_strings)


    def set_target_error_bytes_strings(self, bytes_strings):
        self._target_error_bytes_strings = set(bytes_strings)

    def set_client_error_bytes_strings(self, bytes_strings):
        self._client_error_bytes_strings = set(bytes_strings)

    def set_error_bytes_strings(self, bytes_strings):
        self._error_bytes_strings = set(bytes_strings)



    def contains_iteraror(self, bytes_iterator):
        return self._responce_bytes.contains_iterator(bytes_iterator)

    def target_reached(self):
        return self.contains_iteraror(self._target_reached_bytes_strings)

    def success(self):
        return self.contains_iteraror(self._success_bytes_strings)

    def failure(self):
        return self.contains_iteraror(self._failure_bytes_strings)

    def wait_error(self):
        return self.contains_iteraror(self._wait_error_bytes_strings)

    def not_found_error(self):
        return self.contains_iteraror(self._not_found_error_bytes_strings)

    def access_denied_error(self):
        return self.contains_iteraror(self._access_denied_error_bytes_strings)

    def target_error(self):
        target_errors_bool = [
            self.wait_error(),
            self.not_found_error(),
            self.access_denied_error(),
            self.contains_iteraror(self._target_error_bytes_strings)
        ]
        return any(target_errors_bool)

    def client_error(self):
        return self.contains_iteraror(self._client_error_bytes_strings)

    def error(self):
        errors_bool = [
            self.target_error(),
            self.client_error(),
            self.contains_iteraror(self._error_bytes_strings)
        ]
        return any(errors_bool)
    


if __name__ == "__main__":
    responce_bytes =  ResponceBytes("responce in bytes")

    responce_analyser = ResponceBytesAnalyser(responce_bytes, True)
    responce_analyser.set_success_bytes_strings(["responce"])
    responce_analyser.set_error_bytes_strings(["responce"]) 

    print(responce_analyser.error())