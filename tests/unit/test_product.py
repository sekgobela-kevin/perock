import inspect
import itertools
import unittest
from perock.product import Product
from perock import product

class TestProductSetUp():
    def setUp(self):
        self.items = ["Marry", "Bella", "Paul", "Michael"]
        self.start_ends = (
            (0,2), (2,4),(4,6),(6,8),(8,10), (10,12),
            (12,14),(14,16),(16,18),(18,20)
        )
        self.iterables = self.generate_iterators(self.start_ends)
        self.callables = [
            self.generate_callable(0,2),
            self.generate_callable(2,4),
            self.generate_callable(4,6),
            self.generate_callable(6,8),
            self.generate_callable(8,10),
            self.generate_callable(10,12),
            self.generate_callable(12,14),
            self.generate_callable(14,16),
            self.generate_callable(16,18),
            self.generate_callable(18,20),
        ]

    def assertIterablesEqual(self, iterables, iterables2):
        self.assertEqual(list(iterables), list(iterables2))


    def generate_numbers(self, start, end):
        # Generate numbers(testing purposes)
        for i in range(start, end):
            yield i

    def generate_iterators(self, start_ends):
        # Generate iterators with numbers(testing purposes)
        iterators = []
        for start, end in start_ends:
            iterators.append(self.generate_numbers(start, end))
        return iterators

    def generate_callables(self, start_ends):
        # Generate callables that return numbers(testing purposes)
        # This method does not work
        iterators = []
        for start, end in start_ends:
            def callable():
                # start, end will here may be diferent from one in the loop
                # start, end will the current value when function is called.
                # It would the item of 'start_ends' iterator
                return self.generate_numbers(start, end)
            iterators.append(callable)
            # The time callable() is called, (start,end) would have changed.
            # Its better to use generator(yield)
        return iterators

    def generate_callable(self, start, end):
        def callable():
            return range(start, end)
        return callable


class TestProduct(TestProductSetUp, unittest.TestCase):
    def test_callables_to_iterators(self):
        # Corresponding method is not used
        ...

    def test_is_callables_iterator(self):
        # Corresponding method is not used
        self.assertTrue(Product.is_callables_iterator(self.callables))
        self.assertFalse(Product.is_callables_iterator(self.iterables))
        self.assertFalse(Product.is_callables_iterator([]))

    def test_split_iterator(self):
        iterator = [0,1,2,3,4,5,6]
        self.assertEqual(
            list(Product.split_iterator(iterator,2)), 
            [[0,1],[2,3], [4,5],[6]]
        )

    def test_product_grouped_callables(self):
        # Corresponding method is not used
        pass

    def test_product_double_callables(self):
        callables_product = Product.product_double_callables(*(self.callables[:2]))
        itertools_product = itertools.product(*self.iterables[:2])
        self.assertIterablesEqual(callables_product, itertools_product)

    def test_product_single_callable(self):
        callables_product = Product.product_single_callable(*(self.callables[:1]))
        itertools_product = itertools.product(*self.iterables[:1])
        self.assertIterablesEqual(callables_product, itertools_product)


    def test_flatten_callable_product(self):
        def callable():
            return ( ((1,2),(2,3),) ,((5,6),))
        flat = Product.flatten_callable_product(callable)
        self.assertIterablesEqual(flat, ((1,2, 2,3),(5,6)))


    def test_product_three_callables(self):
        callables_product = Product.product_three_callables(self.callables[:3])
        itertools_product = itertools.product(*self.iterables[:3])
        self.assertIterablesEqual(callables_product, itertools_product)


    def test_product_four_callables(self):
        callables_product = Product.product_four_callables(self.callables[:4])
        itertools_product = itertools.product(*self.iterables[:4])
        self.assertIterablesEqual(callables_product, itertools_product)
    

    def test_product_callables_recursive(self):
        # Test with 4 callables
        callables_product = Product.product_callables_recursive(self.callables[:4])
        itertools_product = itertools.product(*self.iterables[:4])
        self.assertIterablesEqual(callables_product, itertools_product)

        with self.assertRaises(Exception):
            Product.product_callables_recursive(self.callables[:10])


            
    def test_product_callables_recursive_advanced(self):
        callables_product = Product.product_callables_recursive_advanced(
            self.callables
        )
        itertools_product = itertools.product(*self.iterables)
        self.assertIterablesEqual(callables_product, itertools_product)


    def test_product_repeat_callables(self):
        def callable():
            return [0,1,2]
        repeated = list(Product.product_repeat_callables([callable], 2))
        self.assertEqual(len(repeated), 2)
        self.assertIterablesEqual(repeated[0](), itertools.product([0,1,2]))
        self.assertIterablesEqual(repeated[1](), itertools.product([0,1,2]))
    
    def test_product_callables_repeat(self):
        callables_product = Product.product_callables_repeat(
            self.callables[:2], repeat=3
        )
        itertools_product = itertools.product(*self.iterables[:2], repeat=3)
        self.assertIterablesEqual(callables_product, itertools_product)

    def test_product_callables(self):
        callables_product = Product.product_callables(
            self.callables[:2], repeat=2
        )
        itertools_product = itertools.product(*self.iterables[:2], repeat=2)
        self.assertIterablesEqual(callables_product, itertools_product)

        
    def test_product(self):
        callables_product = Product.product(
            *self.callables[:2], repeat=2
        )
        self.assertNotIsInstance(callables_product, itertools.product)
        itertools_product = itertools.product(*self.iterables[:2], repeat=2)
        self.assertIterablesEqual(callables_product, itertools_product)

        iterators = [range(0,5),range(5,10)]
        self.assertIterablesEqual(
            itertools.product(*iterators, repeat=2),
            Product.product(*iterators, repeat=2)
        )


class TestFunctions(TestProductSetUp, unittest.TestCase):
    def test_product(self):
        callables_product = product.product(
            *self.callables[:2], repeat=2
        )
        self.assertNotIsInstance(callables_product, itertools.product)
        itertools_product = itertools.product(*self.iterables[:2], repeat=2)
        self.assertIterablesEqual(callables_product, itertools_product)

        iterators = [range(0,5),range(5,10)]
        self.assertIterablesEqual(
            itertools.product(*iterators, repeat=2),
            product.product(*iterators, repeat=2)
        )
