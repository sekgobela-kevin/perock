import unittest
import itertools
import os

from common_test import CommonTest
from perock import forcetable


folder_path = os.path.split(os.path.abspath(__file__))[0]


class ForcetableSetUp(CommonTest):
    def setUp(self):
        self.setup_fields()
        self.setup_table()

    def setup_fields(self):
        # Create passwords and usernames fields
        self.usernames_field = forcetable.FieldFile(
            "usernames", self.usernames_file_path
        )
        self.passwords_field = forcetable.FieldFile(
            "passwords", self.passwords_file_path
        )
        # Set items name 
        self.usernames_field.set_item_name("username")
        self.passwords_field.set_item_name("password")

    def setup_table(self):
        # enable_callable_product=False
        # Enables use of itertools.product() for cartesian product
        # It should be True if max_parallel_primary_tasks > 1
        self.table = forcetable.Table()
        self.table.add_primary_field(self.usernames_field)
        self.table.add_field(self.passwords_field)


    def tearDown(self):
        self.usernames_field.close()
        self.passwords_field.close()



class TestFieldFileCommon(ForcetableSetUp, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.usernames_file = open(self.usernames_file_path)
        self.passwords_file = open(self.passwords_file_path)

    def setup_fields(self):
        # Create passwords and usernames fields
        self.usernames_field = forcetable.FieldFile(
            "usernames", self.usernames_file_path
        )
        self.passwords_field = forcetable.FieldFile(
            "passwords", self.passwords_file_path
        )
        # Set items name 
        self.usernames_field.set_item_name("username")
        self.passwords_field.set_item_name("password")

    def tearDown(self):
        self.usernames_field.close()
        self.passwords_field.close()

        self.usernames_file.close()
        self.passwords_file.close()


    def test_get_items(self):
        self.assertListEqual(
            list(self.passwords_field.get_items()), self.passwords
        )

    def test_for_exaustion(self):
        # Test if username field does not get exausted after being looped
        first_usernames = list(self.usernames_field.get_items())
        second_usernames = list(self.usernames_field.get_items())
        self.assertGreater(len(first_usernames), 0)
        self.assertListEqual(first_usernames, second_usernames)

    def test_with_itertools_product(self):
        #_product = itertools.product(
        #    self.usernames_file,
        #    self.usernames_file
        #)
        _product = itertools.product(
           self.usernames_field.get_items(),
           self.usernames_field.get_items()
        )

        _expected_product = itertools.product(
            self.usernames,
            self.usernames
        )
        # Its expected for product of FieldFile with itself to be small.
        # That has todo with file position being changed while
        # calculating cartesian product.
        # Thats similar to trying to calculate cartesian product file object
        # with itself.
        # There will be problems with file positions.

        # THis assert tests for restriction.
        self.assertLess(len(list(_product)), len(list(_expected_product)))

    def test_with_itertools_product_second(self):
        _product = itertools.product(
            self.usernames_field.get_items(),
            self.passwords_field.get_items()
        )

        _expected_product = itertools.product(
            self.usernames,
            self.passwords
        )
        # The two products are expected to be equal.
        # usernames_field and passwords_field have opened different
        # file objects.
        # There wont be problems with file positions being changed
        # in unwanted way.
        self.assertListEqual(list(_product), list(_expected_product))



class TestForceTableFunctions(unittest.TestCase):
    def setUp(self):
        # Column items
        self.usernames = ["Marry", "Bella", "Michael"]
        self.passwords = ["1234", "0000", "th234"]

        # Creates fields for table
        self.usernames_field = forcetable.Field('usernames', self.usernames)
        self.usernames_field.set_primary()
        # Sets key name to use in record key in Table
        self.usernames_field.set_item_name("username")
        self.passwords_field = forcetable.Field('passwords', self.passwords)
        self.passwords_field.set_item_name("password")

        self.dict_records = [
            {'password': '1234', 'username': 'Marry'}, 
            {'password': '1234', 'username': 'Bella'}, 
            {'password': '1234', 'username': 'Michael'}, 
            {'password': '0000', 'username': 'Marry'}, 
            {'password': '0000', 'username': 'Bella'}, 
            {'password': '0000', 'username': 'Michael'}, 
            {'password': 'th234', 'username': 'Marry'}, 
            {'password': 'th234', 'username': 'Bella'}, 
            {'password': 'th234', 'username': 'Michael'}
        ]

        fixtures_folder = os.path.join(folder_path, "fixtures")
        self.json_file_path = os.path.join(fixtures_folder, "table.json")
        self.csv_file_path = os.path.join(fixtures_folder, "table.csv")

        assert os.path.isfile(self.json_file_path), self.json_file_path
        assert os.path.isfile(self.csv_file_path), self.csv_file_path

        # Creates Table object
        self.setup_table()

        self.records = self.table.get_records()

    def setup_table(self):
        # Creates Table object
        self.table = forcetable.Table()
        # Set common record to be shared by all records
        #self.common_record = forcetable.Record()
        #self.common_record.add_item("submit", "login")
        #self.table.set_common_record(self.common_record)
        # Add fields to table
        self.table.add_field(self.usernames_field)
        self.table.add_field(self.passwords_field)

    def test_json_to_table(self):
        table = forcetable.json_to_table(self.json_file_path)
        self.assertIsInstance(table, forcetable.Table)
        self.assertCountEqual(
            table.get_records(), self.table.get_records()
        )

    def test_csv_to_table_fp(self):
        with open(self.csv_file_path) as fp:
            table = forcetable.csv_to_table_fp(fp)
            self.assertIsInstance(table, forcetable.Table)
            self.assertCountEqual(
                table.get_records(), self.table.get_records()
            )      

    def test_csv_to_table(self):
        table = forcetable.csv_to_table(self.csv_file_path)
        self.assertIsInstance(table, forcetable.Table)
        self.assertCountEqual(
            table.get_records(), self.table.get_records()
        )



if __name__ == '__main__':
    unittest.main()