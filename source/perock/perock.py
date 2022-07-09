from io import FileIO
import os
from . import forcetable


def read_file_lines(path):
    '''Reads lines from file in path, returns generator'''
    with open(path, "r") as f:
        for line in f:
            yield line.strip("\n")

def file_to_field(path, name=None):
    '''Creates Field object from file in path'''
    items = read_file_lines(path)
    if name == None:
        # filename with extension
        filename = os.path.split(path)
        # filename without extension
        name = os.path.splitext(filename)[0]
    return forcetable.Field(name, items)
