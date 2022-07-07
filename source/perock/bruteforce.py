from typing import Type

from . import attack
from . import bforce
from . import forcetable


class BruteForce(attack.Attack, bforce.BForce):
    # Corresponding classes to be used by this class
    base_attack_class = attack.Attack
    base_bforce_class = bforce.BForce

    def __init__(self, target, table, optimise=True) -> None:
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

    def set_session(self, session):
        # Sets session object to be used by Attack objects
        self.base_bforce_class.set_session(session)

    def get_session(self):
        # Get session set on the object
        self.base_bforce_class.get_session(self)

    def close_session(self):
        # Closes session se on the object
        self.base_bforce_class.close_session(self)
    
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

from . import target
class TestBruteForce(BruteForce):
    def __init__(self, target, table, optimise=True) -> None:
        super().__init__(target, table, optimise)

    def __attack__init__(self, *args, **kwargs):
        super().__attack__init__(*args, **kwargs)
        self.responce: target.Responce
        self.name = "name"

    def success(self):
        print(self.data)
        return False

    def request(self):
        return target.Target().login({})


if __name__ == "__main__":
    #attack_class = BruteForce(attack.Attack, forcetable.FTable())
    #print(attack_class.start())
    usernames = ["Marry", "Bella", "Michael"]
    passwords = range(100000)

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

    bforce.start()
    print()
