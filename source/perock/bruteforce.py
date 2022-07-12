'''
Defines High level classes built on top Attack and BForce classes

This module is an attempt combine/merge Attack classes and BForce
classes into one single class. Its built on top of Attack class or
similar classes and BForce class or similar classes.

BForce and Attack class server different purposes but things
can be much easier if the two classes were to be merged. This module
attempts to perform using inheritance but with restrictions.

BruteForce class inherits both Attack and BForce classes. BForce class
instances requires Attack class to function. Since BruteForce is inherits
Attack class, it becomes possible to dynamically create Attack class
BruteForce through inheritance.

The created Attack clas is the one that internally set as Attack class
to be used by BruteForce class. 

There may be restrictions or overhead from the tricks used. If classes
here do not work, its better to to use corresponding classes in 
'bforce' module such as BForce, BForceAsync.

Author: Sekgobela Kevin
Date: July 2022
Languages: Python 3
'''
from typing import Type

from . import attack
from . import bforce
from . import forcetable


class BruteForceBase():
    '''High level class for performing bruteforce attack.
    
    This class is a combination of both Attack and BForce class or 
    similar classes. Unlike BForce or similar classes, objects of this
    class do not require setting of attack class.
    
    Attack class will be created on fly based on this class. This class
    serves as Attack class and or BForce class which relieves us from 
    having to set Attack class manually.
    
    This may come with overhead or restrictions as this class inherits from
    classes that are not same or even similar. Methods belonging to 
    Attack class does not have access to some attributes of instances 
    of this class.
    
    Those methods will be executed within Attack object not within 
    this classes instances. Attack class methods are not usable in
    this class but BForce class methods can be used as in BForce
    class.'''
    base_attack_class: Type[attack.Attack]
    base_bforce_class = Type[bforce.BForce]

    def __init__(self, target, table, optimise=True):
        '''
        target: 
            System or target to attack e.g webpage(url)
        table: 
            Table object or collection of Record objects

        optimise: 
            True if should perfom optimisations based items of 'table' argument.
 
        'optimise' allows skipping of some records based on other records that 
        were cracked. E.g username needs passwords combination needs to be 
        tried until username matches one of passwords but should stop as
        soon as theres a match.

        Its not worth it to continue trying combination of passwords while
        username already matched one of passwords. Its better to set
        'optimise' as True for username-password attack.
        '''
        super().__init__("test target", forcetable.Table())
        self.target = target
        self.table: forcetable.Table = table
        self.optimise = optimise

        self.bforce = self._create_bforce_object(
            self.target, self.table, self.optimise
        )

    def __attack__init__(self, target, data):
        '''
        Method called on __init__() of created attack objects
        
        Use this method to setup variables to be used on with attack
        object. This method may be called on different thread or proccess
        so care should be taken when using it.
        
        Its safe to use attaributes of attack object as it will executed
        with attack object.'''
        self.base_attack_class.__init__(self, target, data)

    def __bforce__init__(self, *args, **kwargs):
        '''Method called on __init__() of this object'''
        self.base_bforce_class.__init__(self, *args, **kwargs)

    @classmethod
    def _create_bforce_object(cls, *args, **kwargs) -> bforce.BForce:
        bforce = cls.base_bforce_class(*args, **kwargs)
        attack_class = cls._create_attack_class()
        bforce.set_attack_class(attack_class)
        return bforce

    
    def set_max_parallel_tasks(self, total_tasks: int):
        '''Sets maximum number of tasks to run in parallel'''
        self.bforce.set_max_parallel_tasks(total_tasks)

    def set_max_workers(self, max_workers: int):
        '''Sets maximum workers to use to execute tasks in parallel'''
        self.set_max_workers(max_workers)

    def set_executor(self, executor):
        '''Sets executor to use to execute tasks'''
        self.bforce.set_executor(executor)

    

class BruteForce(BruteForceBase, attack.Attack):
    # Corresponding classes to be used by this class
    base_attack_class = attack.Attack
    base_bforce_class = bforce.BForce

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

    def start(self):
        self.bforce.start()


class BruteForceAsync(BruteForceBase, attack.AttackAsync):
    # Corresponding classes to be used by this class
    base_attack_class = attack.AttackAsync
    base_bforce_class = bforce.BForceAsync

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

    async def start(self):
        await self.bforce.start()

class BruteForceBlock(BruteForceBase, attack.Attack):
    # Corresponding classes to be used by this class
    base_attack_class = attack.Attack
    base_bforce_class = bforce.BForce

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

if __name__ == "__main__":
    from . import target
    class TestBruteForce(BruteForceAsync):
        def __init__(self, target, table, optimise=True) -> None:
            super().__init__(target, table, optimise)

        def __attack__init__(self, *args, **kwargs):
            super().__attack__init__(*args, **kwargs)
            self.responce: target.Responce
            self.name = "name"

        def success(self):
            return True

        async def request(self):
            #print("request", self.data)
            return target.Target().login({})


        import asyncio

    #attack_class = BruteForce(attack.Attack, forcetable.Table())
    #print(attack_class.start())
    usernames = ["Marry", "Bella", "Michael"]
    passwords = range(10000000)

    # Creates fields for table
    usernames_col = forcetable.Field('usernames', usernames)
    # Sets key name to use in record key in Table
    usernames_col.set_item_name("username")
    passwords_col = forcetable.Field('passwords', passwords)
    passwords_col.set_item_name("password")

    table = forcetable.Table()
    # Set common record to be shared by all records
    common_record = forcetable.Record()
    common_record.add_item("submit", "login")
    table.set_common_record(common_record)
    # Add fields to table
    table.add_primary_field(usernames_col)
    table.add_field(passwords_col)

    bforce = TestBruteForce("", table, False)


    bforce.start()
