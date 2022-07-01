import unittest

from perock.forcetable import FRow
from perock.forcetable import FColumn
from perock.forcetable import FTable

from perock import forcetable 


class TestFRowCommon():
    def setUp(self):
        self.items = {
            "Name": "John Doe",
            "Age": 80,
            "Country": "USA",
            "Race": "European"
        }
        self.frow = FRow(self.items)
        self.empty_frow = FRow()

    def test_add_item(self):
        self.frow.add_item("Gender", "Male")
        self.assertIn("Gender", self.frow)
    
    def test_add_items(self):
        self.frow.add_items({"Gender": "Male"})
        self.assertEqual(len(self.frow), len(self.items)+1)

    def test_set_items(self):
        self.empty_frow.set_items(self.items)
        self.assertEqual(len(self.empty_frow), len(self.items))

    def test_get_item(self):
        self.assertEqual(self.frow.get_item("Name"), self.items["Name"])

    def test_get_items(self):
        self.assertEqual(self.frow.get_items(), self.items)


class TestFColumnCommon():
    def setUp(self):
        self.items = ["Marry", "Bella", "Paul", "Michael"]
        self.fcolumn = FColumn("names", self.items)

    def test_set_name(self):
        self.fcolumn.set_name("peoples_names")
        self.assertEqual(self.fcolumn.get_name(), "peoples_names")

    def test_set_item_name(self):
        self.fcolumn.set_item_name("name")
        self.assertEqual(self.fcolumn.get_item_name(), "name")

    def test_get_items(self):
        self.assertEqual(self.fcolumn.get_items(), self.items)
    
    def test_get_name(self):
        self.assertEqual(self.fcolumn.get_name(), "names")

    def get_item_name(self):
        with self.assertRaises(Exception):
            # Column item name wasnt set
            self.fcolumn.get_item_name()
        self.fcolumn.set_item_name("name")
        self.assertEqual(self.fcolumn.get_item_name(), "name")

    def test_set_primary(self):
        self.fcolumn.set_primary()
        self.assertTrue(self.fcolumn.is_primary())

    def test_unset_primary(self):
        self.fcolumn.set_primary()
        self.fcolumn.unset_primary()
        self.assertFalse(self.fcolumn.is_primary())

    def test_is_primary(self):
        self.fcolumn.set_primary()
        self.assertTrue(self.fcolumn.is_primary())
        self.fcolumn.unset_primary()
        self.assertFalse(self.fcolumn.is_primary())



class TestFTableCommon(unittest.TestCase):
    def setUp(self):
        # Column items
        self.usernames = ["Marry", "Bella", "Michael"]
        self.passwords = ["1234", "0000", "th234"]

        # Creates columns for table
        self.usernames_column = FColumn('usernames', self.usernames)
        self.usernames_column.set_primary()
        # Sets key name to use in row key in Table
        self.usernames_column.set_item_name("username")
        self.passwords_column = FColumn('passwords', self.passwords)
        self.passwords_column.set_item_name("password")

        # Creates FTable object
        self.ftable = FTable()
        # Set common row to be shared by all rows
        self.common_row = FRow()
        self.common_row.add_item("submit", "login")
        self.ftable.set_common_row(self.common_row)
        # Add columns to table
        self.ftable.add_column(self.usernames_column)
        self.ftable.add_column(self.passwords_column)

        # FTable object without FColumns
        self.empty_ftable = FTable()

        self.dict_frows = [
            {'password': '1234', 'submit': 'login', 'username': 'Marry'}, 
            {'password': '1234', 'submit': 'login', 'username': 'Bella'}, 
            {'password': '1234', 'submit': 'login', 'username': 'Michael'}, 
            {'password': '0000', 'submit': 'login', 'username': 'Marry'}, 
            {'password': '0000', 'submit': 'login', 'username': 'Bella'}, 
            {'password': '0000', 'submit': 'login', 'username': 'Michael'}, 
            {'password': 'th234', 'submit': 'login', 'username': 'Marry'}, 
            {'password': 'th234', 'submit': 'login', 'username': 'Bella'}, 
            {'password': 'th234', 'submit': 'login', 'username': 'Michael'}
        ]

    def test_set_primary_column(self):
        self.empty_ftable.set_primary_column(self.usernames_column)
        self.assertIn(self.usernames_column, self.empty_ftable.get_columns())

    def test_primary_column_exists(self):
        self.assertTrue(self.ftable.primary_column_exists())
        self.assertFalse(self.empty_ftable.primary_column_exists())
        self.empty_ftable.add_column(self.passwords_column)
        # passwords_column is not primary column
        self.assertFalse(self.empty_ftable.primary_column_exists())


    def test_add_column(self):
        self.empty_ftable.add_column(self.passwords_column)
        self.assertIn(self.passwords_column, self.empty_ftable.get_columns())
        self.empty_ftable.add_column(self.usernames_column)
        # Primary column exists as self.usernames_column is primary column
        self.assertTrue(self.empty_ftable.primary_column_exists())

        

    def test_add_primary_column(self):
        self.empty_ftable.add_primary_column(self.passwords_column)
        self.assertIn(self.passwords_column, self.empty_ftable.get_columns())
        self.assertTrue(self.empty_ftable.primary_column_exists())


    def test_get_primary_columns(self):
        self.assertCountEqual(self.ftable.get_primary_columns(), [self.usernames_column])
        self.assertCountEqual(self.empty_ftable.get_primary_columns(), [])

    def test_get_primary_column(self):
        self.assertEqual(self.ftable.get_primary_column(), self.usernames_column)
        self.assertEqual(self.ftable.get_primary_column(), self.usernames_column)

    def test_get_columns(self):
        self.assertCountEqual(self.ftable.get_columns(), [self.usernames_column, 
        self.passwords_column])
        self.assertCountEqual(self.empty_ftable.get_columns(), [])


    def test_get_rows(self):
        self.assertCountEqual(self.ftable.get_rows(), self.dict_frows)
        self.assertCountEqual(self.empty_ftable.get_rows(), [])


    def test_get_column_names(self):
        self.assertCountEqual(self.ftable.get_column_names(), ["passwords", 
        "usernames"])
        self.assertCountEqual(self.empty_ftable.get_column_names(), [])

    def test_get_item_names(self):
        self.assertCountEqual(self.ftable.get_item_names(), ["password", 
        "username"])
        self.assertCountEqual(self.empty_ftable.get_item_names(), [])

    def test_get_columns_items(self):
        self.assertCountEqual(self.ftable.get_columns_items(), [self.passwords, 
        self.usernames])
        self.assertCountEqual(self.empty_ftable.get_columns_items(), [])

    def get_primary_items(self):
        self.assertEqual(self.ftable.get_primary_items(), self.usernames)
        self.assertEqual(self.empty_ftable.get_primary_items(), None)


    def test_dicts_to_rows(self):
        frows = list(self.ftable.dicts_to_rows(self.dict_frows))
        self.assertIsInstance(frows[0], FRow)
        self.assertEqual(len(frows), len(self.dict_frows))

    def rows_to_dicts(self):
        frows = list(self.ftable.dicts_to_rows(self.dict_frows))
        dicts = list(self.ftable.rows_to_dicts(frows))
        self.assertIsInstance(frows[0], dict)
        self.assertEqual(len(frows), len(dicts))


    def test_columns_to_rows(self):
        frows = self.ftable.dicts_to_rows(self.dict_frows)
        columns = [self.usernames_column, self.passwords_column]
        self.assertCountEqual(self.ftable.columns_to_rows(columns, self.common_row), 
        frows)
        self.assertCountEqual([], [])

    def test_set_common_row(self):
        self.empty_ftable.set_common_row(self.common_row)
        self.assertEqual(self.empty_ftable.get_common_row(), self.common_row)

    def test_get_common_row(self):
        self.assertEqual(self.empty_ftable.get_common_row(), FRow())
        self.assertEqual(self.ftable.get_common_row(), self.common_row)

    def test_update_rows(self):
        # Hard to test(shouldnt be public method)
        pass

    def test_update(self):
        # Hard to test(shouldnt be public method)
        pass


class TestFunctions(unittest.TestCase):
    def setUp(self):
        # Column items
        self.usernames = ["Marry", "Bella", "Michael"]
        self.passwords = ["1234", "0000", "th234"]

        # Creates columns for table
        self.usernames_column = FColumn('usernames', self.usernames)
        self.usernames_column.set_primary()
        # Sets key name to use in row key in Table
        self.usernames_column.set_item_name("username")
        self.passwords_column = FColumn('passwords', self.passwords)
        self.passwords_column.set_item_name("password")

        self.columns = [self.usernames_column, self.passwords_column]

        self.frow = FRow({'password': '1234', 'submit': 'login', 'username': 'Bella'})
        self.frow2 = FRow({'password': 'th234', 'submit': 'login', 'username': 'Marry'})


    def test_get_row_primary_item(self):
        frow_item = forcetable.get_row_primary_item(self.frow, self.usernames_column)
        self.assertEqual(frow_item, 'Bella')
        frow_item = forcetable.get_row_primary_item(self.frow2, self.usernames_column)
        self.assertEqual(frow_item, 'Marry')


    def test_row_primary_included(self):
        is_included = forcetable.row_primary_included(self.frow, 
        self.usernames_column, self.usernames_column.get_items())
        self.assertTrue(is_included)

        is_included = forcetable.row_primary_included(self.frow, 
        self.usernames_column, self.passwords_column.get_items())
        self.assertFalse(is_included)



class TestFRow(TestFRowCommon, unittest.TestCase):
    pass


class TestFColumn(TestFColumnCommon, unittest.TestCase):
    pass

class TestFTable(TestFTableCommon, unittest.TestCase):
    pass