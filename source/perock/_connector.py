from perock import _util


class BaseConnector():
    '''Class methods for connecting to target with record'''
    @classmethod
    def _create_session(cls, *args, **kwargs):
        return cls.create_session(cls, *args, **kwargs)

    @classmethod
    def _connect(cls, target, record, session=None):
        cls._before_connect()
        response = cls.connect(target, record, session)
        cls._after_connect()
        return response

    @classmethod
    def _after_connect(cls):
        cls.after_connect()

    @classmethod
    def _before_connect(cls):
        cls.before_connect()

    @classmethod
    def create_session(cls, *args, **kwargs):
        '''Creates session for connecting to target'''
        raise NotImplementedError

    @classmethod
    def connect(cls, target, record, session=None):
        '''Connects to target and return response'''
        raise NotImplementedError

    @classmethod
    def after_connect(cls):
        '''Called after connecting to target'''
        raise NotImplementedError

    @classmethod
    def before_connect(cls):
        '''Called before connecting to target'''
        raise NotImplementedError



class Connector(BaseConnector):
    '''Class methods for connecting to target with record'''
    pass


class AsyncConnector(BaseConnector):
    '''Class methods for connecting to target with record'''
    @classmethod
    async def _connect(cls, target, record, session=None):
        await cls._before_connect()
        await cls.connect(target, record, session)
        await cls._after_connect()

    @classmethod
    async def _before_connect(cls):
        await _util.call_function(cls.before_connect)

    @classmethod
    async def _after_connect(cls):
        await _util.call_function(cls.after_connect)
