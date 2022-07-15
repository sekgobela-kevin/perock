import os
from perock import forcetable


# Sets up paths needed by this file
folder_path = os.path.split(os.path.abspath(__file__))[0]
asserts_path = os.path.join(folder_path, "asserts")

usernames_file = os.path.join(asserts_path, "usernames.txt")
passwords_file = os.path.join(asserts_path, "passwords.txt")


# Creates fields to be used in table
with open(usernames_file) as f:
    # Creates fields from file lines
    usernames_field = forcetable.Field("usernames", f)

with open(passwords_file) as f:
    passwords_field = forcetable.Field("passwords", f)

# FieldFile is better as removes leading space characters
usernames_field = forcetable.FieldFile("usernames", usernames_file)
passwords_field = forcetable.FieldFile("passwords",passwords_file)

# Create list with the fields
fields = [usernames_field, passwords_field]


# Now let create table object from fields
# table = forcetable.Table(fields)
table = forcetable.Table()
# table.add_fields(fields)
table.add_field(usernames_field)
table.add_field(passwords_field)

# Get records from table
# Records will be created from cartesian product of records
records = table.get_records()
# Table is also iterable
records = iter(table)

print(list(records)[:2])
# [{'usernames': 'SMITH\n', 'passwords': 'foobar\n'}, 
# {'usernames': 'SMITH\n', 'passwords': 'flyers\n'}]


# Realise how records were created automatically for you.
# You dont need to use itertools.product()

# You could also manually create records without fields
# Record is just similar to dict(it inherits dictionary)
record = forcetable.Record({"username": "user23", "password": "12345"})
print(record)
# {"username": "user23", "password": "12345"}


# Here another feature table
# We can set record to merged into each created record of table
table.set_common_record(forcetable.Record({"action": "login"}))
print(list(table)[:2])
# [{'passwords': 'foobar', 'action': 'login', 'usernames': 'SMITH'}, 
# {'passwords': 'foobar', 'action': 'login', 'usernames': 'JOHNSON'}]


# We can also set keys in records to be different from fields names
# We need to set that within the fields themselfs
# Let update the fields
usernames_field.set_item_name("username")
passwords_field.set_item_name("password")
print(list(table)[:2])
# [{'password': 'foobar', 'action': 'login', 'username': 'SMITH'}, 
# {'password': 'foobar', 'action': 'login', 'username': 'JOHNSON'}]