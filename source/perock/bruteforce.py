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

    def __init__(self, target, table, optimise):
        '''
        target: 
            System or target to attack e.g webpage(url)
        table: 
            FTable object or collection of FRow objects

        optimise: 
            True if should perfom optimisations based items of 'table' argument.
 
        'optimise' allows skipping of some rows based on other rows that 
        were cracked. E.g username needs passwords combination needs to be 
        tried until username matches one of passwords but should stop as
        soon as theres a match.

        Its not worth it to continue trying combination of passwords while
        username already matched one of passwords. Its better to set
        'optimise' as True for username-password attack.
        '''
        # Calls __init__() of the base classes
        #self.__attack__init__(None, None)
        self.__bforce__init__(target, table, not optimise)

        self.target = target
        self.table: forcetable.FTable = table

        # Set attack_class needed by BForce instances
        self.set_attack_class(self._create_attack_class())

    def __attack__init__(self, *args, **kwargs):
        # Method called on __init__() of created attack objects
        self.base_attack_class.__init__(self, *args, **kwargs)

    def __bforce__init__(self, *args, **kwargs):
        # Method called on __init__() of this object
        self.base_bforce_class.__init__(self, *args, **kwargs)
    
    @classmethod
    def _create_attack_class(cls) -> Type[attack.Attack]:
        # Creates Attack class from current class
        class AttackClass(cls):
            def __init__(self, *args, **kwargs) -> None:
                self.__attack__init__(*args, **kwargs)
        return AttackClass

    @classmethod
    def _create_bforce_class(cls) -> Type[bforce.BForce]:
        # Creates BForce class from current class
        # This method is not used.
        class BforceClass(cls):
            def __init__(self, *args, **kwargs) -> None:
                self.base_bforce_class.__init__(self, *args, **kwargs)
        return BforceClass


class BruteForce(BruteForceBase, bforce.BForce, attack.Attack):
    # Corresponding classes to be used by this class
    base_attack_class = attack.Attack
    base_bforce_class = bforce.BForce

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

class BruteForceAsync(
        BruteForceBase, 
        bforce.BForceAsync,
        attack.AttackAsync):
    # Corresponding classes to be used by this class
    base_attack_class = attack.AttackAsync
    base_bforce_class = bforce.BForceAsync

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

class BruteForceBlock(
        BruteForceBase, 
        bforce.BForceBlock,
        attack.Attack):
    # Corresponding classes to be used by this class
    base_attack_class = attack.Attack
    base_bforce_class = bforce.BForce

    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

from . import target
class TestBruteForce(BruteForceAsync):
    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

    def __attack__init__(self, *args, **kwargs):
        super().__attack__init__(*args, **kwargs)
        self.responce: target.Responce
        self.name = "name"

    def success(self):
        return False

    async def request(self):
        #print("request", self.data)
        return target.Target().login({})


if __name__ == "__main__":
    import asyncio

    #attack_class = BruteForce(attack.Attack, forcetable.FTable())
    #print(attack_class.start())
    usernames = ["Marry", "Bella", "Michael"]
    passwords = range(100)

    # Creates columns for table
    usernames_col = forcetable.FColumn('usernames', usernames)
    # Sets key name to use in row key in Table
    usernames_col.set_item_name("username")
    passwords_col = forcetable.FColumn('passwords', passwords)
    passwords_col.set_item_name("password")

    table = forcetable.FTable()
    # Set common row to be shared by all rows
    common_row = forcetable.FRow()
    common_row.add_item("submit", "login")
    table.set_common_row(common_row)
    # Add columns to table
    table.add_primary_column(usernames_col)
    table.add_column(passwords_col)

    bforce = TestBruteForce("", table, True)


    
    bforce.set_max_workers(10)

    asyncio.run(bforce.start())
    print()
