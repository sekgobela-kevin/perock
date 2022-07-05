'''
Defines utility classes or functions to be used by other modules
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''
import asyncio
import time
import contextvars
import functools


async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


def group_generator(generator, group_size):
    generator_group = []
    for value in generator:
        generator_group.append(value)
        if len(generator_group) == group_size:
            yield generator_group.copy()
            generator_group.clear()
    if generator_group:
        yield generator_group


def split_iterator(iterator, split_size):
    return iter(group_generator(iterator, split_size))

def iscallable(referance):
    # Returns True if referance is callable
    type_str = str(type(referance))
    if "function" in type_str:
        return True
    elif "method" in type_str:
        return True
    else:
        return False


if __name__ == "__main__":
    print(list(split_iterator([1,2,4,6,8,10], 4)))
    pass