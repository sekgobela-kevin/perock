'''
Contain classes for creating target for testing purposes
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from typing import Iterable
from .forcetable import FRow


class Account(FRow):
    '''Represents account information of item in item'''
    def __init__(self, items={}) -> None:
        super().__init__(items)


class Target():
    '''Base class for creating target'''
    def __init__(self, accounts: Iterable[Account]=[]) -> None:
        self._accounts = list(accounts)

    def add_account(self, account):
        # Adds account to target
        if self.account_valid_form(account):
            if not self.account_exists(account):
                self._accounts.append(account)
        else:
            err_msg = "Account is not in valid form"
            raise ValueError(err_msg, account)

    def remove_account(self, account):
        # Removes account from target
        if self.account_exists(account):
            self._accounts.remove(account)
        else:
            err_msg = "Account not found"
            raise Exception(err_msg, account)

    def account_exists(self, account):
        # Checks if account exists
        return account in self._accounts

    def success_responce(self, account):
        return f"The system was unlocked with {account}"

    def fail_responce(self, account):
        return f"Failed to log into system with given credentials"

    def access_denied_responce(self, account):
        return f"Access to the system was denied"

    def target_error_responce(self, account):
        return "Our system experienced errors, caused by our side."

    def client_error_responce(self, account):
        return "Theres problem with your account info"

    def account_success(self, account):
        # Checks if account is valid in the system
        # That means the account can log to system
        return self.account_exists(account)

    def account_valid_form(self, account):
        # Validate account to check if account is in valid form
        return isinstance(account, Account)

    def target_error_detected(self, account):
        # Returns True if target experienced errors
        return not self.account_valid_form(account)

    def client_error_detected(self, account):
        # Returns True if client request is malformed
        return False

    def access_denied(self, account):
        # Returns True if access is denied.
        return not self.account_valid_form(account)


    def login(self, account):
        # Logs into target with account
        if self.access_denied(account):
            return self.access_denied_responce(account)
        elif self.client_error_detected(account):
            return self.client_error_responce(account)
        elif self.target_error_detected(account):
            return self.target_error_responce(account)
        elif self.account_success(account):
            return self.success_responce(account)
        else:
            return self.fail_responce(account)
            #err_msg = "Unknown error during loging into target"
            #raise Exception(err_msg, account)

        

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
    print(target.login(account1))

    # The system wont be unlocked as account2 is not added
    print(target.login([]))
