import os
from . import forcetable


def read_file_lines(path):
    '''Reads lines from file in path, returns generator'''
    with open(path, "r") as f:
        #yield from f
        for line in f:
            yield line.strip()

def file_to_column(path, name=None):
    '''Creates FColumn object from file in path'''
    items = read_file_lines(path)
    if name == None:
        # filename with extension
        filename = os.path.split(path)
        # filename without extension
        name = os.path.splitext(filename)[0]
    return forcetable.FColumn(name, items)

class FColumnFile(forcetable.FColumn):
    '''Class for creating column items from file in path''' 
    def __init__(self, name, path) -> None:
        file_lines = read_file_lines(path)
        super().__init__(name, file_lines)
