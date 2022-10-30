class PerockError(Exception):
    '''Perock base exception class'''

class BruteError(PerockError):
    '''Error relating to perock brute-forcing'''

class ResponseError(PerockError):
    '''Error relating to response'''

class UnexpectedError(PerockError):
    '''Something unexpected happened'''

class ConnectorError(PerockError):
    '''Something is wrong with connector'''

class UnexpectedResponseError(BruteError):
    '''Response from connector is unexpected'''

class MissingAttackType(PerockError):
    '''Attack class/type is missing'''
