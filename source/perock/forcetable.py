'''
Defines classes for operating with input data for attack
such as 'usernames' and 'passwords'. Data is represented
as table like with columns being things like iterator of
'passwords' and row being combination of column items.

Rows are made up of combination of columns items. Row can be 
represented as map like {'username': 'john43', 'password': 'rj235'}.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from typing import Iterator, Set
import itertools


class FColumn():
    '''Class for operating with column data. Column data  
    may include things like 'passwords', 'usernames', etc.'''
    def __init__(self, name, items) -> None:
        '''
        Creates FColumn object
        Parameters
        ----------
        name: str
            Name of column
        items: Iterator
            Iterator with items of column
        '''
        # Stores items of column, e.g 'passwords'
        self.items = items
        # Name of column
        self.name = name
        # Name of each item of column
        # Usually singular of coulun name e.g 'password'
        self.item_name = None

        self.primary = False

    def __iter__(self) -> Iterator:
        return iter(self.items)

    def set_name(self, name):
        '''Sets name of column, e.g 'usernames\''''
        self.name = name

    def set_item_name(self, name):
        '''Sets name for refering to each/one item of column. e.g column name 
        may be 'passwords' but each of them be \'password\''''
        self.item_name = name

    def get_items(self):
        '''Returns items of column'''
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
        # Sets the column as primary column
        self.primary = True

    def unset_primary(self):
        # Unset column as primary column
        self.primary = False

    def is_primary(self):
        # Returns True if column is primary column
        return self.primary




class FRow(dict):
    '''Class for operating with row data. Row data represents
    records to be sent to target, e.g 'password' and 'username'.'''
    def __init__(self, items={}) -> None:
        '''
        Creates FRow object from dictionary
        Parameters
        ----------
        items: Dict
            (optional) Dictionary/map with row items
        '''
        super().__init__(items)

    def add_item(self, name, value):
        '''Adds item to row'''
        self[name] = value
    
    def add_items(self, items):
        '''Adds items to row'''
        self.update(items)

    def set_items(self, items):
        '''Sets/overides row items with specified items'''
        self.update({})
        self.update(items)

    def get_item(self, name):
        return self.get(name)

    def get_items(self):
        return dict(self)


class FTable():
    '''Represents table with data for performing attack'''
    def __init__(self, columns=[]) -> None:
        '''
        Creates table with data for performing attack.
        Parameters
        ----------
        columns: Iterator
            Iterator with FColumn objects
        '''
        # Stores rows of table
        self.columns: Set[FColumn] = set(columns)
        # Stores row with items to be shared by all rows
        self.common_row = FRow()
        # Stores rows of table
        self.rows: Set[FRow] = set()
        # Updates rows to match with couluns
        self.update_rows()

        self.primary_columns: Set[FColumn] = set()
        self.primary_column: FColumn = None

    def set_primary_column(self, column):
        '''Set the column as primary column'''
        self.primary_column = column
        self.columns.add(column)

    def primary_column_exists(self):
        '''Checks if table ha sprimary column'''
        return self.primary_column != None


    def add_column(self, column):
        '''Adds a coulumn to table'''
        if column.is_primary():
            # adds column to primary columns
            self.primary_columns.add(column)
            self.set_primary_column(column)
        self.columns.add(column)
        # Updates rows to use the new column
        self.update()

    def add_primary_column(self, column):
        '''Add the column and make it one of primary columns'''
        self.primary_columns.add(column)
        self.set_primary_column(column)
        self.add_column(column)
        self.update()

    def get_primary_columns(self):
        '''Returns primary column'''
        return self.primary_columns

    def get_primary_column(self):
        '''Returns primary column'''
        return self.primary_column

    def get_columns(self):
        '''Returns primary columns'''
        return self.columns


    def get_rows(self):
        '''Returns rows of the table'''
        return self.rows


    def get_column_names(self):
        '''Returns names of columns in table'''
        return {column.get_name() for column in self.columns}

    def get_item_names(self, force=False):
        '''Returns item names from table columns'''
        return {column.get_item_name(force) for column in self.columns}

    def get_columns_items(self):
        '''Returns items of columns in table'''
        return [column.get_items() for column in self.columns]

    def get_primary_items(self):
        '''Returns items of primary column'''
        if self.primary_column_exists():
            return self.primary_column.get_items()
        else:
            return None


    @staticmethod
    def dicts_to_rows(dicts):
        '''Returns iterable of rows from iterable of dictionaries'''
        # Using map has advantage of using [FRow(dict_) for dict_ in dicts]
        # Map will save memory(uses iterators than just list)
        # 'dicts' can sometimes be large in Millions or Billions
        return map(lambda dict_: FRow(dict_), dicts)

    @staticmethod
    def rows_to_dicts(rows):
        '''Returns iterable of dictionaries from iterable of rows'''
        # This is not worth it as FRow is instance of 'dict'
        return map(lambda row: dict(row), rows)


    @classmethod
    def columns_to_rows(cls, columns, common_row=FRow()):
        '''Returns rows from columns'''
        # Get columns item names(will act as keys)
        # 'item_name' is more suitable than 'name'(name of coulumn)
        column_names = [column.get_item_name(True) for column in columns]
        # Get columns items(act as values)
        columns_items = [column.get_items() for column in columns]
        # Use itertools.product() to get combination of values
        for columns_items in itertools.product(*columns_items):
            if not columns_items:
                break
            # Creates empty row object
            row = FRow()
            # Link back column items to their column names
            # and then add results to row
            for index, column_item in enumerate(columns_items):
                # Adds column name and column item to row
                row.add_item(column_names[index], column_item)
                # Adds also common row to the row
                row.add_items(common_row)
            # itertools.product() output can be larger
            # Appending 'row' to collection is waste of memory
            yield row

    def set_common_row(self, row):
        '''Sets row with items to be shared by all rows'''
        self.common_row = row
        # update rows to use the new common row
        self.update()

    def get_common_row(self):
        return self.common_row

    def update_rows(self):
        '''Updates table rows to keep-up with columns'''
        self.rows = self.columns_to_rows(self.columns, self.common_row)

    def update(self):
        '''Updates table including its rows'''
        # Theres nothing to be updated than just the rows
        self.update_rows()

    def __iter__(self) -> Iterator[FRow]:
        return iter(self.rows)



def get_row_primary_item(row, primary_column):
    '''Returns primary item from row'''
    column_name = primary_column.get_item_name(True)
    # Rember that FRow is instance of dict
    primary_item = row[column_name]
    return primary_item


def row_primary_included(row, primary_column, primary_column_items):
    '''Returns True if primary item of row is in primary_column_items'''
    primary_item = get_row_primary_item(row, primary_column)
    return primary_item in primary_column_items





if __name__ == "__main__":
    usernames = ["david", "marry", "pearl"]*1
    passwords = ["1234", "0000", "th234"]

    # Creates columns for table
    usernames_col = FColumn('usenames', usernames)
    # Sets key name to use in row key in Table
    usernames_col.set_item_name("username")
    passwords_col = FColumn('passwords', passwords)
    passwords_col.set_item_name("password")

    table = FTable()
    # Set common row to be shared by all rows
    common_row = FRow()
    common_row.add_item("submit", "login")
    table.set_common_row(common_row)
    # Add columns to table
    table.add_column(usernames_col)
    table.add_column(passwords_col)
    # print the rows with common row
    # Realise that the keys match ones set by set_item_name()
    print(list(table))
