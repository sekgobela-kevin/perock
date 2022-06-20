'''
Prepares and handles data for attack(e.g usernames, passwords).
That may include finding combination(e.g combination of usernames and 
passwords). 

Other things may include reading data from files and transforming
it in a way that is suitable for attack. e.g 'passwords' and 'usernames' 
may be resolved into individual 'username' and 'password'.

Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
from typing import Dict
import itertools


def transform_to_map(**kwargs):
    '''Converts provided keywords argumnets into map(dict)
    >>> transform_to_map(username="Marry", password="qwer")
    {"username":"Marry", "password":"qwer"}
    '''
    return kwargs

def create_login_data(login_items:Dict, **shared_items):
    '''Creates dictionary with data to log into system. This 
    is for single session or attempt.
    >>> data = {"username":"Marry", password:"qwer"}
    >>> create_login_data(data, submit="login"})
    {"username":"Marry", "password":"qwer", "submit":"login"}'''
    return {**login_items, **shared_items}

def create_logins_data(attack_map:Dict, **shared_data):
    '''Creates collection with data for attempting to log
    into system. Use transform_to_map() function to create
    from input data.
    >>> usernames = ["Marry", "Pearl"]
    >>> passwords = [1111, 1234]
    >>> attack_map = transform_to_map(
        username = usernames,
        password = passwords
    )
    >>> create_logins_data(attack_map, submit="login")
    [{'username': 'Marry', 'password': 1111, 'submit':'login'}, 
    {'username': 'Marry', 'password': 1234, 'submit':'login'}, 
    {'username': 'Pearl', 'password': 1111, 'submit':'login'}, 
    {'username': 'Pearl', 'password': 1234, 'submit':'login'}]
    '''
    map_keys = attack_map.keys()
    map_values = attack_map.values()
    # Use itertools.product() to get combination of values
    for item_values in itertools.product(*map_values):
        # Link the keys to corresponding values
        # Also convert results into dictionary
        login_items = {}
        for index, key in enumerate(map_keys):
            login_items[key] = item_values[index]
        login_data = create_login_data(login_items, **shared_data)
        # itertools.product() output can be larger
        # Appending 'login_data' to collection is waste of memory
        yield login_data
    # This line is waste of bytes
    # I dont know if its possible for generator func to return None
    # Rather return empty list([]) than None
    return list()


 


if __name__ == "__main__":
    passwords = [1111, 3333]
    usernames = ["Marry", "James"]
    coulumn_data = transform_to_map(username=usernames, password=passwords, )
    print(list(create_logins_data(coulumn_data)))

