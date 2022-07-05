import unittest
import os

import perock

folder_path = os.path.split(os.path.abspath(__file__))[0]


class CommonTest():
    @classmethod
    def setUpClass(cls) -> None:
        cls.usernames_folder = os.path.join(folder_path, "fixtures", "usernames")
        cls.passwords_folder = os.path.join(folder_path, "fixtures", "passwords")

        cls.passwords_file_path = os.path.join(
            cls.passwords_folder, 
            "passwords.txt"
        )
        cls.usernames_file_path = os.path.join(
            cls.usernames_folder, 
            "usernames.txt"
        )

        assert os.path.isfile(cls.passwords_file_path), cls.passwords_file_path
        assert os.path.isfile(cls.usernames_file_path), cls.usernames_file_path

        cls.passwords_file_paths = cls.get_files(cls.passwords_folder)
        cls.usernames_file_paths = cls.get_files(cls.usernames_folder)


    @classmethod
    def get_files(cls, folder):
        file_paths = []
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_paths.append(file_path)
        return file_paths

