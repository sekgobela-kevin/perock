import unittest
import itertools
import os

from .common_test import CommonTest
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

