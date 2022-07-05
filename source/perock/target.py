'''
Contain classes for creating target for testing purposes
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from typing import Iterable
import time 

from .forcetable import FRow


class Responce():
    def __init__(self, message, status=None) -> None:
        self._message = message
        self._status = status
        self._closed = False

    def set_message(self, message):
        self._message = message

    def get_message(self):
        return self._message

    def set_status(self, status):
        return self._status

    def get_status(self):
        return self._status
    
    def close(self):
        self._closed = True

    @property
    def closed(self):
        return self._closed


class Account(FRow):
    '''Represents account information of item in item'''
    def __init__(self, items={}) -> None:
        super().__init__(items)


class Target():
    '''Base class for creating target'''
    def __init__(self, accounts: Iterable[Account]=[]) -> None:
        self._accounts = list(accounts)
        self._responce_time = 0
    
    def set_responce_time(self, seconds):
        # Sets to sleep while waiting creating responce
        self._responce_time = seconds

    def get_responce_time(self):
        return self._responce_time

    def get_accounts(self):
        # Returns accounts stored by target
        return self._accounts

    def add_account(self, account):
        # Adds account to target
        if self.account_valid_form(account):
            if not self.account_exists(account):
                self._accounts.append(account)
        else:
            err_msg = "Account{} is not in valid form"
            raise ValueError(err_msg, account)

    def add_accounts(self, accounts):
        # Adds accounts to target
        for account in accounts:
            self.add_account(account)

    def remove_account(self, account):
        # Removes account from target
        if self.account_exists(account):
            self._accounts.remove(account)

    def account_valid_form(self, account):
        # Validate account to check if account is in valid form
        return isinstance(account, Account)

    def account_exists(self, account):
        # Checks if account exists
        if self.account_valid_form(account):
            return account in self._accounts
        else:
            err_msg = "Account not found"
            raise Exception(err_msg, account)

    def success_responce(self, account):
        message = f"The system was unlocked with {account}"
        return Responce(message, 200)

    def error_responce(self, account):
        message = f"Failed to log into system with given credentials"
        return Responce(message, 200)

    def access_denied_responce(self, account):
        message = f"Access to the system was denied"
        return Responce(message, 403)

    def target_error_responce(self, account):
        message = "Our system experienced errors"
        return Responce(message, 500)

    def client_error_responce(self, account):
        message = "Theres problem with your account info"
        return Responce(message, 400)

    def account_success(self, account):
        # Checks if account is valid in the system
        # That means the account can log to system
        return self.account_exists(account)

    def account_fail(self, account):
        # Checks if account not valid in the system
        # That means the account cannot be used to log to system
        return not self.account_success(account)

    def target_error_detected(self, account):
        # Returns True if target experienced errors
        return False

    def client_error_detected(self, account):
        # Returns True if client request is malformed
        return not self.account_valid_form(account)

    def access_denied(self, account):
        # Returns True if access is denied.
        return not self.account_valid_form(account)


    def login(self, account):
        # Logs into target with account
        time.sleep(self._responce_time)
        if self.access_denied(account):
            return self.access_denied_responce(account)
        elif self.client_error_detected(account):
            return self.client_error_responce(account)
        elif self.target_error_detected(account):
            return self.target_error_responce(account)
        elif self.account_fail(account):
            return self.error_responce(account)
        elif self.account_success(account):
            return self.success_responce(account)
        else:
            err_msg = "Unknown error during loging into target"
            raise Exception(err_msg, account)

        

if __name__ == "__main__":

    # Create account1
    account1 = Account()
    account1.add_item("username", "Marry")
    account1.add_item("password", ".234duct")

    # Create account1
    account2 = Account()
    account2.add_item("username", "David")
    account2.add_item("password", "nhs149.89")

    # Create target and add account1
    target = Target()
    target.add_account(account1)

    # The system should be unlocked as account1 was added
    print(target.login(account1).get_message())

    # The system wont be unlocked as account2 is not added
    print(target.login(3).get_message())
