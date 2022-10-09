import unittest

from perock.forcetable import Record, RecordsTable
from perock.forcetable import Field
from perock.forcetable import Table
from perock.forcetable import PrimaryTable

from perock import forcetable 


class TestRecordCommon():
    def setUp(self):
        self.items = {
            "Name": "John Doe",
            "Age": 80,
            "Country": "USA",
            "Race": "European"
        }
        self.record = Record(self.items)
        self.empty_record = Record()

    def test_add_item(self):
        self.record.add_item("Gender", "Male")
        self.assertIn("Gender", self.record)
    
    def test_add_items(self):
        self.record.add_items({"Gender": "Male"})
        self.assertEqual(len(self.record), len(self.items)+1)

    def test_set_items(self):
        self.empty_record.set_items(self.items)
        self.assertEqual(len(self.empty_record), len(self.items))

    def test_get_item(self):
        self.assertEqual(self.record.get_item("Name"), self.items["Name"])

    def test_get_items(self):
        self.assertEqual(self.record.get_items(), self.items)


class TestFieldCommon():
    def setUp(self):
        self.items = ["Marry", "Bella", "Paul", "Michael"]
        self.field = Field("names", self.items)

    def test_set_name(self):
        self.field.set_name("peoples_names")
        self.assertEqual(self.field.get_name(), "peoples_names")

    def test_set_item_name(self):
        self.field.set_item_name("name")
        self.assertEqual(self.field.get_item_name(), "name")

    def test_read_items(self):
        self.assertEqual(self.field.read_items(), self.items)

    def test_get_items(self):
        self.assertEqual(self.field.get_items(), self.items)
    
    def test_get_name(self):
        self.assertEqual(self.field.get_name(), "names")

    def test_get_item_name(self):
        with self.assertRaises(Exception):
            # Field item name wasnt set
            self.field.get_item_name()
        # Field name should be returned when field item name not set
        # and force is True.
        self.assertEqual(self.field.get_item_name(True), "names")
        self.field.set_item_name("name")
        self.assertEqual(self.field.get_item_name(), "name")

    def test_set_primary(self):
        self.field.set_primary()
        self.assertTrue(self.field.is_primary())

    def test_unset_primary(self):
        self.field.set_primary()
        self.field.unset_primary()
        self.assertFalse(self.field.is_primary())

    def test_is_primary(self):
        self.field.set_primary()
        self.assertTrue(self.field.is_primary())
        self.field.unset_primary()
        self.assertFalse(self.field.is_primary())



class TestTableSetUp():
    def setUp(self):
        # Column items
        self.usernames = ["Marry", "Bella", "Michael"]
        self.passwords = ["1234", "0000", "th234"]

        # Creates fields for table
        self.usernames_field = Field('usernames', self.usernames)
        self.usernames_field.set_primary()
        # Sets key name to use in record key in Table
        self.usernames_field.set_item_name("username")
        self.passwords_field = Field('passwords', self.passwords)
        self.passwords_field.set_item_name("password")

        # Creates Table object
        self.create_table_objects()

        self.dict_records = [
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

    def create_table_objects(self):
        # Creates Table object
        self.table = Table()
        # Set common record to be shared by all records
        self.common_record = Record()
        self.common_record.add_item("submit", "login")
        self.table.set_common_record(self.common_record)
        # Add fields to table
        self.table.add_field(self.usernames_field)
        self.table.add_field(self.passwords_field)

        # Table object without Fields
        self.empty_table = Table()
