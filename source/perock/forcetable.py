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
from io import FileIO
from typing import Callable, Iterable, Iterator, Set

from . import product
from . import util


class Field():
    '''Class for operating with field data. Column data  
    may include things like 'passwords', 'usernames', etc.'''
    def __init__(self, name, items) -> None:
        '''
        Creates Field object
        Parameters
        ----------
        name: str
            Name of field
        items: Iterator
            Iterator or callable returning items of field
        '''
        # Stores items of field, e.g 'passwords'
        self.items = items
        # Name of field
        self.name = name
        # Name of each item of field
        # Usually singular of coulun name e.g 'password'
        self.item_name = None

        self.primary = False

    def __iter__(self) -> Iterator:
        return iter(self.get_items())

    def set_name(self, name):
        '''Sets name of field, e.g 'usernames\''''
        self.name = name

    def set_item_name(self, name):
        '''Sets name for refering to each/one item of field. e.g field name 
        may be 'passwords' but each of them be \'password\''''
        self.item_name = name

    def items_callable(self):
        '''Returns True if items are in callable'''
        return util.iscallable(self.items)

    def get_items(self):
        '''Returns items of field'''
        if self.items_callable():
            return self.items()
        else:
            return self.items

    
    def get_name(self):
        '''Returns name of coulumn, e.g 'usernames\''''
        return self.name

    def get_item_name(self, force=False):
        '''Returns item name of coulumn items, e.g 'username\''''
        if self.item_name:
            return self.item_name
        elif force:
            return self.name
        else:
            err_msg = "Column item name wasnt set"
            raise Exception(err_msg)

    def set_primary(self):
        # Sets the field as primary field
        self.primary = True

    def unset_primary(self):
        # Unset field as primary field
        self.primary = False

    def is_primary(self):
        # Returns True if field is primary field
        return self.primary


class FieldFile(Field):
    '''Class for creating field items from file in path''' 
    def __init__(self, name, path) -> None:
        self._path = path
        self._file = open(path)
        super().__init__(name, self._read_file_lines_callable)

    def read_file_lines(self):
        '''Reads lines from file in path, returns generator'''
        for line in self._file:
            line_ = line.rstrip("\n")
            if line_:
                yield line_

    def _read_file_lines_callable(self):
        self._file.seek(0)
        return self.read_file_lines()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._file.close()



class Record(dict):
    '''Class for operating with record data. Row data represents
    records to be sent to target, e.g 'password' and 'username'.'''
    def __init__(self, items={}) -> None:
        '''
        Creates Record object from dictionary
        Parameters
        ----------
        items: Dict
            (optional) Dictionary/map with record items
        '''
        super().__init__(items)

    def add_item(self, name, value):
        '''Adds item to record'''
        self[name] = value
    
    def add_items(self, items):
        '''Adds items to record'''
        self.update(items)

    def set_items(self, items):
        '''Sets/overides record items with specified items'''
        self.clear()
        self.update(items)

    def get_item(self, name):
        return self.get(name)

    def get_items(self):
        return dict(self)


class Table():
    '''Represents table with data for performing attack'''
    def __init__(self, fields=[], enable_callable_product=True) -> None:
        '''
        Creates table with data for performing attack.
        Parameters
        ----------
        fields: Iterator
            Iterator with Field objects
        enable_callable_product: Bool
            Enables cartesian product of field to be calculated differently
            without use of itertools.product().
            A different implementation of similar to that of itertools.product()
            will be used which uses recursion and callable objects.
        '''
        # Stores fields of table
        self.fields: Set[Field] = set(fields)
        # Stores record with items to be shared by all records
        self.common_record = Record()
        # Enables use of callable product over itertools.product()
        self.enable_callable_product = enable_callable_product
        # Stores records of table
        self.records: Iterator[Record] = iter([])

        self.primary_fields: Set[Field] = set()
        self.primary_field: Field = None

        # Add fields to table
        # 'self.fields: Set[Field] = set(fields)' is not enough
        self.add_fields(self.fields)

    def set_primary_field(self, field):
        '''Set the field as primary field'''
        self.primary_field = field
        self.fields.add(field)

    def primary_field_exists(self):
        '''Checks if table ha sprimary field'''
        return self.primary_field != None


    def add_field(self, field):
        '''Adds a coulumn to table'''
        if field.is_primary():
            # adds field to primary fields
            self.primary_fields.add(field)
            self.set_primary_field(field)
        self.fields.add(field)
        # Updates records to use the new field

    def add_fields(self, fields):
        '''Adds multiple field to table'''
        for field in fields:
            self.add_field(field)

    def add_primary_field(self, field):
        '''Add the field and make it one of primary fields'''
        self.primary_fields.add(field)
        self.set_primary_field(field)
        self.fields.add(field)

    def get_primary_fields(self):
        '''Returns primary field'''
        return self.primary_fields

    def get_primary_field(self):
        '''Returns primary field'''
        return self.primary_field

    def get_fields(self):
        '''Returns primary fields'''
        return self.fields

    def get_records(self):
        '''Returns records of the table'''
        # Update records before returning them
        self.update()
        return self.records


    def get_field_names(self):
        '''Returns names of fields in table'''
        return {field.get_name() for field in self.fields}

    def get_item_names(self, force=False):
        '''Returns item names from table fields'''
        return {field.get_item_name(force) for field in self.fields}

    def get_fields_items(self):
        '''Returns items of fields in table'''
        return [field.get_items() for field in self.fields]

    def get_primary_items(self):
        '''Returns items of primary field'''
        if self.primary_field_exists():
            return self.primary_field.get_items()
        else:
            return None


    @staticmethod
    def dicts_to_records(dicts):
        '''Returns iterable of records from iterable of dictionaries'''
        # Using map has advantage of using [Record(dict_) for dict_ in dicts]
        # Map will save memory(uses iterators than just list)
        # 'dicts' can sometimes be large in Millions or Billions
        return map(lambda dict_: Record(dict_), dicts)

    @staticmethod
    def records_to_dicts(records):
        '''Returns iterable of dictionaries from iterable of records'''
        # This is not worth it as Record is instance of 'dict'
        return map(lambda record: dict(record), records)


    @classmethod
    def fields_to_records(cls, 
    fields, 
    common_record=Record(),
    enable_callable_product=True):
        '''Returns records from fields'''
        # Cast to list to maintain order of the fields
        fields = list(fields)
        # Get fields item names(will act as keys)
        # 'item_name' is more suitable than 'name'(name of coulumn)
        field_names = [field.get_item_name(True) for field in fields]
        if enable_callable_product:
            # Appends callables into fields_items
            # Different implementation will be used for cartesian product
            fields_items = [field.get_items for field in fields]
        else:
            # Appends field items into fields_items
            # itertools.product() will be used for cartesian product
            fields_items = [field.get_items() for field in fields]
        # product.product() is just wrapper around Product.product_callable()
        # and itertools.product()
        # product.product() will choose which to used based on fields_items
        # If fields_items contain iterators then itertools.product()
        for fields_items in product.product(*fields_items):
            if not fields_items:
                break
            # Creates empty record object
            record = Record()
            # Link back field items to their field names
            # and then add results to record
            for index, field_item in enumerate(fields_items):
                # Adds field name and field item to record
                record.add_item(field_names[index], field_item)
                # Adds also common record to the record
                record.add_items(common_record)
            # itertools.product() output can be larger
            # Appending 'record' to collection is waste of memory
            yield record

    @classmethod
    def fields_to_records_primary_grouped(
        cls, 
        fields: Set[Field], 
        primary_field: Field, 
        common_record=Record(),
        enable_callable_product=True):
        primary_items = primary_field.get_items()
        # other_fields needs to exclude primary field
        other_fields = fields.copy()
        other_fields.discard(primary_field)
        # Loop each of primary field items
        primary_grouped_records = []
        if primary_field not in fields:
            err_msg = "primary_field not in fields"
            raise ValueError(err_msg)
        if len(fields) == 1:
            records = cls.fields_to_records(
                fields, common_record, enable_callable_product
            )
            # All items of primary record are treated as group
            yield records
        else:
            for primary_item in primary_items:
                # Creates field for primary field
                # Name of field is taken from primary field
                field = Field(primary_field.get_name(), [primary_item])
                field.set_item_name(primary_field.get_item_name(True))
                # Merge the field with other fields
                fields = other_fields.union([field])
                # Creates records the fields
                records =  cls.fields_to_records(
                    fields, common_record, enable_callable_product
                )
                yield records
        return primary_grouped_records

    def records_primary_grouped(self):
        if self.primary_field_exists():
            return self.fields_to_records_primary_grouped(
                self.fields,
                self.primary_field,
                self.common_record,
                self.enable_callable_product
            )
        else:
            err_msg = "Primary field is needed, but not found"
            raise Exception(err_msg)

    def set_common_record(self, record):
        '''Sets record with items to be shared by all records'''
        self.common_record = record
        

    def get_common_record(self):
        '''Gets record to be merged with each record'''
        return self.common_record

    def update_records(self):
        '''Updates table records to keep-up with fields'''
        self.records = self.fields_to_records(
            self.fields, 
            self.common_record,
            self.enable_callable_product
        )

    def update(self):
        '''Updates table including its records'''
        # Theres nothing to be updated than just the records
        self.update_records()

    def __iter__(self) -> Iterator[Record]:
        return iter(self.get_records())


class MapTable(Table):
    '''Dynamically records based on primary field items'''
    def __init__(self, fields=[], enable_callable_product=True) -> None:
        super().__init__(fields, enable_callable_product)
        self.fields_callable = None

    def set_fields_callable(self, __callable: Callable):
        self.fields_callable = __callable

    # def primary_item_to_records(self, primary_item):
    #     '''Creates records from primary item'''
    #     if self.records_callable != None:
    #         # Create records from provided callable
    #         records =  self.records_callable(primary_item)
    #     else:
    #         # Creates field for primary field
    #         # Name of field is taken from primary field
    #         field = Field(self.primary_field.get_name(), [primary_item])
    #         field.set_item_name(self.primary_field.get_item_name(True))
    #         # Get all other field excluding primary fileld
    #         other_fields = self.fields.difference([self.primary_field])
    #         # Merge the field with other fields
    #         fields = other_fields.union([field])
    #         # Creates records the fields
    #         records =  self.fields_to_records(
    #             fields, self.common_record, self.enable_callable_product
    #         )
    #     return records

    # def primary_item_to_records(self, primary_item) -> Iterator[Record]:
    #     if self.records_callable != None:
    #         # Call the prvided callable to get records from primary item
    #         return self.records_callable(primary_item, self.common_record)
    #     else:
    #         # Return empty iterator if callable not provided
    #         return iter([])

    def primary_item_to_fields(self, primary_item) -> Iterator[Record]:
        if self.fields_callable != None:
            # Call the prvided callable to get records from primary item
            return self.fields_callable(primary_item)
        else:
            # Return empty iterator if callable not provided
            return iter([])

    def records_primary_grouped(self):
        if self.primary_field_exists():
            primary_field_name = self.primary_field.get_name()
            primary_field_item_name = self.primary_field.get_item_name(True)
            for primary_item in self.primary_field.get_items():
                # Get the fields to create records from
                fields = set(self.primary_item_to_fields(primary_item))
                # Primary field shouldnt be included(removed it)
                fields.discard(self.primary_field)
                # Uses table to convert the fields to records
                table = Table(fields)
                # Create field for representing item
                item_field = Field(primary_field_name, [primary_item])
                item_field.set_item_name(primary_field_item_name)
                # Now add the field to the table
                table.add_field(item_field)
                # Provides table with common record
                table.set_common_record(self.common_record)
                # Return records from table created from the fields
                yield table.get_records()
        else:
            err_msg = "Primary field is required, but not found"
            raise Exception(err_msg)

    def update_records(self):
        '''Updates table records to keep-up with fields'''
        # Update records only if there are fields in table
        def records_callable():
            # Flattens primary grouped records
            for records in self.records_primary_grouped():
                for record in records:
                    yield record
        # Updates update records with with generator function
        self.records = records_callable()


def get_record_primary_item(record, primary_field):
    '''Returns primary item from record'''
    field_name = primary_field.get_item_name(True)
    # Rember that Record is instance of dict
    primary_item = record[field_name]
    return primary_item


def record_primary_included(record, primary_field, primary_field_items):
    '''Returns True if primary item of record is in primary_field_items'''
    primary_item = get_record_primary_item(record, primary_field)
    return primary_item in primary_field_items





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
