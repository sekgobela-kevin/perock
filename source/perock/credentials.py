'''
Represents and generate data to be sent to target/system.
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from typing import Iterator
import handle_data
import util


def create_credentials(raw_data, extra_data={}):
    '''Creates Credential objects raw_data
    'raw_data' : Map with data for creating Credential objects.
    'extra_items' : Map with extra data to add to each Credential
    object
    
    >>> raw_data = {"password":[123,111], "username":["Marry", "Hope"]}
    >>> list(create_credentials(raw_data ,{"submit":"login"}))
    [{'password': 123, 'username': 'Marry', 'submit': 'login'}, 
    {'password': 123, 'username': 'Hope', 'submit': 'login'}, 
    {'password': 111, 'username': 'Marry', 'submit': 'login'}, 
    {'password': 111, 'username': 'Hope', 'submit': 'login'}]
    '''
    logins_data = handle_data.create_logins_data(
        raw_data, **extra_data
    )
    for login_data in logins_data:
        yield Credential(login_data, extra_data)
    return list()


def group_credentials(credentials, group_size=1000):
    return util.group_generator(credentials, group_size)


class Credential(dict):
    '''Represents data to be used to log into system'''
    def __init__(self, login_items, extra_data={}) -> None:
        '''
        'login_items' : Map with data items to log with.
        'extra_data' : Extra items to add to login_items'''
        super().__init__({**login_items, **extra_data})



class Credentials():
    '''Represents credentials to be used to log into system'''
    def __init__(self, raw_data, extra_data={}) -> None:
        '''
        'raw_data' : Map for creating data for loging into system. The
        map could contain keys like 'passwords' and 'usernames'.
        'extra_items' : Extra items to add to login_items
        
        >>> raw_data = {"password":[123,111], "username":["Marry", "Hope"]}
        >>> list(Credentials(raw_data ,{"submit":"login"}))
        [{'password': 123, 'username': 'Marry', 'submit': 'login'}, 
        {'password': 123, 'username': 'Hope', 'submit': 'login'}, 
        {'password': 111, 'username': 'Marry', 'submit': 'login'}, 
        {'password': 111, 'username': 'Hope', 'submit': 'login'}]
        '''
        self.raw_data = raw_data
        self.extra_data = extra_data

    def __iter__(self) -> Iterator[Credential]:
        self.credentials = create_credentials(
            self.raw_data, self.extra_data
        )
        return iter(self.credentials)



class GroupedCredentials():
    '''Represents iterator of Credentials objects'''
    def __init__(self, raw_data, extra_data={}, group_size=1000) -> None:
        self.raw_data = raw_data
        self.extra_data = extra_data
        self.group_size = group_size

    def __iter__(self) -> Iterator[Credential]:
        self.credentials = create_credentials(
            self.raw_data, self.extra_data
        )
        return iter(group_credentials(self.credentials, self.group_size))

    



if __name__ == "__main__":
    names = ["david", "marry", "pearl"]*10000
    passwords = ["1234", "0000", "th234"]
    credentials_obj = GroupedCredentials(
        {"password":names, "username":passwords},{"submit":"login"}
    )
    print(credentials_obj)
