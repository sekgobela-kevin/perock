

class ResponceBytes():
    def __init__(self, __bytes):
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
        return len(filtered) == len(list(bytes_iterator))

    def __str__(self) -> str:
        return self.to_text(self._bytes)

    def __add__(self, other):
        return self.__class__(self.get_bytes() + other.get_bytes())

    def __contains__(self, other):
        if isinstance(other, (str, bytes)):
            return self.to_bytes(other) in self.get_bytes()
        else:
            if self._contains_strict:
                return self.contains_all(other)
            else:
                return self.contains_any(other)

    def __len__(self):
        return len(self._bytes)

    def __iter__(self):
        return iter(self._bytes)


if __name__ == "__main__":
    responce_bytes =  ResponceBytes("responce in bytes")

    print(["responce", b"bytes"] in responce_bytes)