from perock import _checker



class BaseController(_checker.BaseChecker):
    '''Controls what to be done with target, record or response'''
    @classmethod
    def transform_record(cls, record):
        '''Transforms record into format supported by connector'''
        return record

    @classmethod
    def should_connect(cls, target, record):
        '''Decides if record should be connected to target'''
        return True

    @classmethod
    def should_retry(cls, record, response):
        '''Decides if should retry connecting to target'''
        return not cls._target_reached(response)

    @classmethod
    def should_switch(cls, record, response):
        '''Decides if should switch to next primary item records'''
        return False


    


    
