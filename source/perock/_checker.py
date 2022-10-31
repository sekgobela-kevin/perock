import inspect

from perock import _util


class BaseChecker():
    '''Collection of class methods for checking response'''
    @classmethod
    def _connection_started(cls, response):
        return cls.connection_started(response)

    @classmethod
    def _connection_failed(cls, response):
        return cls.connection_failed(response)

    @classmethod
    def _target_reached(cls, response):
        return cls.target_reached(response)

    @classmethod
    def _success(cls, response):
        return cls.success(response)

    @classmethod
    def _failure(cls, response):
        return cls.failure(response)

    @classmethod
    def _target_error(cls, response):
        return cls.target_error(response)

    @classmethod
    def _client_errors(cls, response):
        return cls.client_errors(response)

    @classmethod
    def _errors(cls, response):
        return cls.errors(response)


    @classmethod
    def connection_started(cls, response):
        '''Checks if connection to target was started'''
        responce = cls.attempt_object.get_responce()
        return responce != None


    @classmethod
    def connection_failed(cls, response):
        '''Checks if connection to target failed(likely bacause of exception)'''
        return isinstance(response, Exception)


    @classmethod
    def target_reached(cls, response):
        '''Checks if target was reached through connection'''
        if not cls.connection_started(response):
            return False
        elif cls.connection_failed(response):
            return False
        else:
            return True

    @classmethod
    def success(cls, response):
        '''Checks if there was success after connecting to target'''
        # Success can be guessed from failure
        if cls.target_reached():
            # If theres is no error or failure then it may be success.
            # This should work in most cases.
            return not (cls.success() or cls.errors())
        # Success is not expected if target was reached.
        return False

    @classmethod
    def failure(cls, response):
        '''Checks if there was falure after connecting to target'''
        raise NotImplementedError("'failure' is not implemented")

    @classmethod
    def target_error(cls, response):
        '''Checks if there was error after target was reached'''
        return False

    @classmethod
    def client_errors(cls, response):
        '''Checks if there was error that caused target not to be reached'''
        return cls.connection_started() and not cls.target_reached()

    @classmethod
    def errors(cls, response):
        '''Checks if there was error(target or client errors)'''
        return  cls.client_errors() or cls.target_errors()



class Checker(BaseChecker):
    '''Collection of class methods for checking response'''
    pass


class AsyncChecker(BaseChecker):
    '''Collection of class methods for checking response'''
    @classmethod
    async def _connection_started(cls, response):
        return await _util.call_function(cls.connection_started, response)

    @classmethod
    async def _connection_failed(cls, response):
        return await _util.call_function(cls.connection_failed, response)

    @classmethod
    async def _target_reached(cls, response):
        return await _util.call_function(cls.target_reached, response)

    @classmethod
    async def _success(cls, response):
        return await _util.call_function(cls._success, response)

    @classmethod
    async def _failure(cls, response):
        return await _util.call_function(cls.failure, response)

    @classmethod
    async def _target_error(cls, response):
        return await _util.call_function(cls.target_error, response)

    @classmethod
    async def _client_errors(cls, response):
        return await _util.call_function(cls.client_errors, response)

    @classmethod
    async def _errors(cls, response):
        return await _util.call_function(cls.errors, response)