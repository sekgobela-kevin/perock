import unittest

from perock.forcetable import Record
from perock.forcetable import Field
from perock.forcetable import Table

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

    def test_get_items(self):
        self.assertEqual(self.field.get_items(), self.items)
    
    def test_get_name(self):
        self.assertEqual(self.field.get_name(), "names")

    def get_item_name(self):
        with self.assertRaises(Exception):
            # Column item name wasnt set
            self.field.get_item_name()
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


class TestTableCommon(TestTableSetUp):
    def setUp(self):
        super().setUp()

    def test_set_primary_field(self):
        self.empty_table.set_primary_field(self.usernames_field)
        self.assertIn(self.usernames_field, self.empty_table.get_fields())

    def test_primary_field_exists(self):
        self.assertTrue(self.table.primary_field_exists())
        self.assertFalse(self.empty_table.primary_field_exists())
        self.empty_table.add_field(self.passwords_field)
        # passwords_field is not primary field
        self.assertFalse(self.empty_table.primary_field_exists())


    def test_add_field(self):
        self.empty_table.add_field(self.passwords_field)
        self.assertIn(self.passwords_field, self.empty_table.get_fields())
        self.empty_table.add_field(self.usernames_field)
        # Primary field exists as self.usernames_field is primary field
        self.assertTrue(self.empty_table.primary_field_exists())

        

    def test_add_primary_field(self):
        self.empty_table.add_primary_field(self.passwords_field)
        self.assertIn(self.passwords_field, self.empty_table.get_fields())
        self.assertTrue(self.empty_table.primary_field_exists())


    def test_get_primary_fields(self):
        self.assertCountEqual(self.table.get_primary_fields(), [self.usernames_field])
        self.assertCountEqual(self.empty_table.get_primary_fields(), [])

    def test_get_primary_field(self):
        self.assertEqual(self.table.get_primary_field(), self.usernames_field)
        self.assertEqual(self.table.get_primary_field(), self.usernames_field)

    def test_get_fields(self):
        self.assertCountEqual(self.table.get_fields(), [self.usernames_field, 
        self.passwords_field])
        self.assertCountEqual(self.empty_table.get_fields(), [])


    def test_get_records(self):
        self.assertCountEqual(self.table.get_records(), self.dict_records)
        self.assertCountEqual(self.empty_table.get_records(), [])


    def test_get_field_names(self):
        self.assertCountEqual(self.table.get_field_names(), ["passwords", 
        "usernames"])
        self.assertCountEqual(self.empty_table.get_field_names(), [])

    def test_get_item_names(self):
        self.assertCountEqual(self.table.get_item_names(), ["password", 
        "username"])
        self.assertCountEqual(self.empty_table.get_item_names(), [])

    def test_get_fields_items(self):
        self.assertCountEqual(self.table.get_fields_items(), [self.passwords, 
        self.usernames])
        self.assertCountEqual(self.empty_table.get_fields_items(), [])

    def get_primary_items(self):
        self.assertEqual(self.table.get_primary_items(), self.usernames)
        self.assertEqual(self.empty_table.get_primary_items(), None)


    def test_dicts_to_records(self):
        records = list(self.table.dicts_to_records(self.dict_records))
        self.assertIsInstance(records[0], Record)
        self.assertEqual(len(records), len(self.dict_records))

    def records_to_dicts(self):
        records = list(self.table.dicts_to_records(self.dict_records))
        dicts = list(self.table.records_to_dicts(records))
        self.assertIsInstance(records[0], dict)
        self.assertEqual(len(records), len(dicts))


    def test_fields_to_records(self):
        records = self.table.dicts_to_records(self.dict_records)
        fields = [self.usernames_field, self.passwords_field]
        self.assertCountEqual(self.table.fields_to_records(fields, self.common_record), 
        records)
        self.assertCountEqual([], [])

    def test_set_common_record(self):
        self.empty_table.set_common_record(self.common_record)
        self.assertEqual(self.empty_table.get_common_record(), self.common_record)

    def test_get_common_record(self):
        self.assertEqual(self.empty_table.get_common_record(), Record())
        self.assertEqual(self.table.get_common_record(), self.common_record)

    def test_update_records(self):
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

        # Creates fields for table
        self.usernames_field = Field('usernames', self.usernames)
        self.usernames_field.set_primary()
        # Sets key name to use in record key in Table
        self.usernames_field.set_item_name("username")
        self.passwords_field = Field('passwords', self.passwords)
        self.passwords_field.set_item_name("password")

        self.fields = [self.usernames_field, self.passwords_field]

        self.record = Record({'password': '1234', 'submit': 'login', 'username': 'Bella'})
        self.record2 = Record({'password': 'th234', 'submit': 'login', 'username': 'Marry'})


    def test_get_record_primary_item(self):
        record_item = forcetable.get_record_primary_item(self.record, self.usernames_field)
        self.assertEqual(record_item, 'Bella')
        record_item = forcetable.get_record_primary_item(self.record2, self.usernames_field)
        self.assertEqual(record_item, 'Marry')


    def test_record_primary_included(self):
        is_included = forcetable.record_primary_included(self.record, 
        self.usernames_field, self.usernames_field.get_items())
        self.assertTrue(is_included)

        is_included = forcetable.record_primary_included(self.record, 
        self.usernames_field, self.passwords_field.get_items())
        self.assertFalse(is_included)



class TestRecord(TestRecordCommon, unittest.TestCase):
    pass


class TestField(TestFieldCommon, unittest.TestCase):
    pass

class TestTable(TestTableCommon, unittest.TestCase):
    pass