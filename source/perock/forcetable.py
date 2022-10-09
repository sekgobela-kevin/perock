'''
Defines classes for operating with input data for attack
such as 'usernames' and 'passwords'. Data is represented
as table like with fields being things like iterator of
'passwords' and record being combination of field items.

Rows are made up of combination of fields items. Row can be 
represented as map like {'username': 'john43', 'password': 'rj235'}.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from forcetable import field as Field
from forcetable import file_field as FieldFile
from forcetable import record as Record

from forcetable import table as Table
from forcetable import primary_table as PrimaryTable
from forcetable import records_table as RecordsTable

from forcetable import *


if __name__ == "__main__":
    usernames = ["david", "marry", "pearl"]*1
    passwords = ["1234", "0000", "th234"]

    # Creates fields for table
    usernames_col = Field('usenames', usernames)
    # Sets key name to use in record key in Table
    usernames_col.set_item_name("username")
    passwords_col = Field('passwords', passwords)
    passwords_col.set_item_name("password")

    table = Table()
    # Set common record to be shared by all records
    common_record = Record()
    common_record.add_item("submit", "login")
    table.set_common_record(common_record)
    # Add fields to table
    table.add_field(usernames_col)
    table.add_field(passwords_col)
    # print the records with common record
    # Realise that the keys match ones set by set_item_name()
    print(list(table))
