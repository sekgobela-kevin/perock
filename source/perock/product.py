'''
Calculates cartesian product of iterators similar to `itertools.product()`.

But also allows iterator to be a callable which should return the 
iterator. If 'iterables' does not contain callable objects then 
`itertools.product()` will be used.

If not, cartesian product will be calculated without 'itertools.product()'
using recursion. It ha slimitations in that it may be slower then 
`itertools.product()` and 'RecursionError' ay be raised if callables
or repeat argumnet are 12 or more.

Using `itertools.product()` is better even if it may raise MemoryError
on large iterables.

Author: Sekgobela Kevin
Date: July 2022
Languages: Python 3
'''
from prodius import product


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

    #print(len(list(product_callables_recursive_advanced([gen, gen, gen, gen]))))
    product_ = product(*[gen]*3, repeat=10)

    count = 0
    for item in product_:
        if count == 1000000:
            break
        print(item)
        count+=1