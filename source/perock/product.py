import inspect
import itertools
from typing import Iterator


class Product():
    def __init__(self, *iterables: Iterator, repeat=1) -> None:
        self.iterables = iterables
        self.repeat = repeat

    @classmethod
    def callables_to_iterators(cls, callables):
        # Returns iterators from list of callables
        return [iter(callable()) for callable in callables]

    @classmethod
    def is_callables_iterator(cls, iterator):
        # Returns True if iterator conatin callable objects
        if iterator:
            type_str = str(type(iterator[0]))
            if "function" in type_str:
                return True
            elif "method" in type_str:
                return True
            else:
                return False

    @classmethod
    def split_iterator(cls, iterator, split_size):
        # Split iterator into smaller 2D iterator
        iterator_group = []
        for value in iterator:
            iterator_group.append(value)
            if len(iterator_group) == split_size:
                yield iterator_group.copy()
                iterator_group.clear()
        if iterator_group:
            yield iterator_group

    @classmethod
    def product_grouped_callables(cls, callables, group_size=2):
        # Returns product of grouped callables
        # Method is not used
        grouped_callables =  cls.split_iterator(callables, group_size)
        for callables in grouped_callables:
            if len(callables) == 2:
                product = cls.product_double_callables(*callables)
            elif len(callables) == 1:
                product = cls.product_single_callable(callables[0])
            else:
                raise Exception()
            yield product

    @classmethod
    def product_double_callables(cls, callable1, callable2):
        # Returns product of two iterators in callables
        for item in callable1():
            for item2 in callable2():
                yield (item, item2)

    @classmethod
    def product_single_callable(cls, callable):
        # Returns product of iterator in callable
        for item in callable():
            yield (item,)

    @classmethod
    def flatten_callable_product(cls, callable):
        # Returns product of callable and flatten the product.
        # callable argument may call other callables through recursion
        # until product is returned.
        for product_item in callable():
            product_item_ = []
            # This is an attempt to flatten product_item tuple
            for sub_item in product_item:
                for sub_sub_item in sub_item:
                    product_item_.append(sub_sub_item)
            yield tuple(product_item_)

    @classmethod
    def product_three_callables(cls, callables):
        if not len(callables) == 3:
            err_msg = f"Three(3) callables expected not {len(callables)}"
            raise ValueError(err_msg)
        last_two = callables[-2:]
        rest = callables[:-2]
        def final_callable_product():
            return cls.product_double_callables(*last_two)

        for callable in rest:
            previous_final_callable_product = final_callable_product

            def callable_product():
                return cls.product_single_callable(callable)

            def final_callable_product():
                return cls.product_double_callables(callable_product, 
                previous_final_callable_product)
        return cls.flatten_callable_product(final_callable_product)


    @classmethod
    def product_four_callables(cls, callables):
        if not len(callables) == 4:
            err_msg = f"Four(4) callables expected not {len(callables)}"
            raise ValueError(err_msg)
        last_three_callables = callables[-3:]
        rest_callables = callables[:-3]

        def final_callable_product():
            return cls.product_three_callables(last_three_callables)

        for callable in rest_callables:
            previous_final_callable_product = final_callable_product

            def callable_product():
                return cls.product_single_callable(callable)

            def final_callable_product():
                return cls.product_double_callables(callable_product, 
                previous_final_callable_product)
        return cls.flatten_callable_product(final_callable_product)
    

    @classmethod
    def product_callables_recursive(cls, callables):
        # Returns product of iterables in callables but limited
        # to 5 callables.
        if len(callables) == 0:
            return cls.product_single_callable(lambda :range(0))
        elif len(callables) == 1:
            return cls.product_single_callable(callables[0])
        elif len(callables) == 2:
            return cls.product_double_callables(*callables)
        elif len(callables) == 3:
            return cls.product_three_callables(callables)
        elif len(callables) == 4:
            return cls.product_four_callables(callables)
        else:
            err_msg = "Product of 5 or more iterators is not supported"
            raise Exception(err_msg, len(callables))

            
    @classmethod
    def product_callables_recursive_advanced(cls, callables):
        # Returns product of iterables in callables
        # This function raises recursion error on 12+ callables
        if len(callables) <= 4:
            # Calculates product of 4 or less than iterables
            return cls.product_callables_recursive(callables)
        else:
            # Toatl Itarables that wont be part of group with 4 iterables
            total_leftout_callables = len(callables) % 4
            # Returns 2D iterator with 4 elements in each
            # It wont always be 4 elements on last group
            four_grouped_callables = list(cls.split_iterator(callables, 4))
            # Non zero if last group has elements less than four(4)
            if total_leftout_callables:
                # Gets group with less than 4 elements(callables)
                leftout_callables_group = four_grouped_callables[-1]
                # Gets the rest of callables groups
                rest_callables_groups = four_grouped_callables[:-1]
            else:
                # Theres no leftout callables
                leftout_callables_group = []
                rest_callables_groups = four_grouped_callables

            # Gets last four callables from rest_callables_groups
            last_four_callables_group = rest_callables_groups[-1]
            # Get rest of callables groups excluding last_four_callables_group
            rest_callables_groups = rest_callables_groups[:-1]

            def final_callable_product():
                # This function will be modified on each iteration.
                # Calculates product of callables in last_four_callables_group
                return cls.product_four_callables(last_four_callables_group)

            for callables_group in rest_callables_groups:
                # Store previous referance final_callable_product()
                previous_final_callable_product = final_callable_product

                # Create callable from product of callables_group
                def callable_product():
                    return cls.product_four_callables(callables_group)

                def merge_callable():
                    # Combine callable_product() with previous 
                    # final_callable_product()
                    return cls.product_double_callables(callable_product, 
                    previous_final_callable_product)

                # Modify final_callable_product() to include callable_product()
                def final_callable_product():
                    # Flatten result of merge_callable
                    return cls.flatten_callable_product(merge_callable)

            # Store previous referance final_callable_product()
            previous_final_callable_product_ = final_callable_product

            def final_callable_product():
                # This callable is for including leftout_callables
                # Checks if there were left out callables
                if leftout_callables_group:
                    # Creates callable for the left out callables
                    def leftout_callable():
                        return cls.product_callables_recursive(
                            leftout_callables_group
                        )
                    
                    def merge_callable():
                        # Combine final_callable_product() with leftout_callable()
                        # and return their product.
                        return cls.product_double_callables(
                                previous_final_callable_product_,
                                leftout_callable
                        )
                    # Flatten the product of combination of 
                    # final_callable_product() and leftout_callable()
                    return cls.flatten_callable_product(merge_callable)
                else:
                    return previous_final_callable_product_()     

            return final_callable_product()


    @classmethod
    def product_repeat_callables(cls, callables, repeat):
        # Yields products of callables in 'repeat' times
        for _ in range(repeat):
            def callable_func():
                return cls.product_callables_recursive_advanced(callables)
            yield callable_func
    
    @classmethod
    def product_callables_repeat(cls, callables, repeat):
        # Creates product of iterator in callables
        repeated_callables = list(cls.product_repeat_callables(
            callables, repeat=repeat
        ))        
        #print(list(repeated_callables)[0])
        def recursive_product_callable():
            # Recursion error expected on 12+ callables
            return cls.product_callables_recursive_advanced(repeated_callables)
        # Flattens each product removing unneccessay tuples
        return cls.flatten_callable_product(recursive_product_callable)

    @classmethod
    def product_callables(cls, callables, repeat=1):
        # Creates product of iterator in callables
        return cls.product_callables_repeat(callables, repeat=repeat)

    @classmethod
    def product(cls, *iterables, repeat=1):
        # Returns product of iterators similar to `itertools.product()`.
        # But iterator can also be callables like function.
        if cls.is_callables_iterator(iterables):
            return cls.product_callables(iterables, repeat=repeat)
        else:
            return itertools.product(*iterables, repeat=repeat)


def product(*iterables, repeat=1):
    '''Returns cartesian product of iterators similar to `itertools.product()`.

    But also allows iterator to be a callable which should return the 
    iterator. If 'iterables' does not contain callable objects then 
    `itertools.product()` will be used.
    
    If not, cartesian product will be calculated without 'itertools.product()'
    using recursion. It ha slimitations in that it may be slower then 
    `itertools.product()` and 'RecursionError' ay be raised if callables
    or repeat argumnet are 12 or more.
    
    Using `itertools.product()` is better even if it may raise MemoryError
    on large iterables.'''
    return Product.product(*iterables, repeat=repeat)


if __name__ == "__main__":
    def gen():
        for _ in range(3):
            yield _

    def range_callable(*arg, **kwags):
        return range(1,4000000000)

    def range_callable_2(*arg, **kwags):
        return range(4,700000000000)

    def range_callable_3(*arg, **kwags):
        return range(7,1000000000000000000000)

    #print(len(list(Product.product_callables_recursive_advanced([gen, gen, gen, gen]))))
    product_ = Product.product(*[gen]*3, repeat=10)

    count = 0
    for item in product_:
        if count == 1000000:
            break
        print(item)
        count+=1