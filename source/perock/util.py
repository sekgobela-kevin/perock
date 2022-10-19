'''
Defines utility classes or functions to be used by other modules
Author: Sekgobela Kevin
Date: June 2022
Languages: Python 3
'''


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

def iscallable(__obj):
    # Returns True if object is callable
    #return callable(__obj)
    type_str = str(type(__obj))
    if "function" in type_str:
        return True
    elif "method" in type_str:
        return True
    else:
        return False


def copy_class(class_):
    # Returns copy of class
    class class_copy(class_):
        pass
    return class_copy


def cast_to_class(
        source_class, 
        dest_class,
        excluded=["__class__"],
        magic=False):
    # Casts source_class into dest_class
    # Copy dest_class to avoid mofying original class
    dest_class_copy = copy_class(dest_class)
    for attr in dir(dest_class_copy):
        # Ignore magic methods if magic argument is True
        if attr.startswith("__") and attr.endswith("__"):
            if not magic:
                continue
        # Get corresponding attribute value from source_class
        attr_val = getattr(source_class, attr)
        # Overide attribute with value from this class
        setattr(dest_class_copy, attr, attr_val)
        
    # Returns the class after modifications
    return dest_class_copy



def _try_close(__object):
    # Attempts to close provided object
    try:
        # This should work in most cases
        __object.close()
    except (AttributeError):
        # Context manager may also help in closing object.
        # If it fails then the object cannot be closed.
        try:
            with __object:
                pass
        except (AttributeError):
            pass

async def _async_try_close(__object):
    # Attempts to close provided object asynchonously
    try:
        # This should work in most cases
        await __object.close()
    except (AttributeError, TypeError):
        # Context manager may also help in closing object.
        # If it fails then the object cannot be closed.
        try:
            async with __object:
                # object cannot be closed
                pass
        except (AttributeError, TypeError):
            # Let try close it the usual way 
            _try_close(__object)


def try_close(__object, raise_exception=True):
    try:
        _try_close(__object)
    except Exception as e:
        if raise_exception: raise e

async def async_try_close(__object, raise_exception=True):
    try:
        await _async_try_close(__object)
    except Exception as e:
        if raise_exception: raise e


if __name__ == "__main__":
    print(list(split_iterator([1,2,4,6,8,10], 4)))
    pass