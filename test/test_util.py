# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from pymurgy.util import *


class TestUtil(unittest.TestCase):
    def test_is_instance_of_name(self):
        subClass = SubClass(1, 2)
        self.assertTrue(is_instance_of_name(subClass, "SuperClass"))
        self.assertTrue(is_instance_of_name(subClass, "SubClass"))
        self.assertTrue(is_instance_of_name(subClass, "object"))
        superClass = SuperClass(3)
        self.assertTrue(is_instance_of_name(superClass, "SuperClass"))
        self.assertFalse(is_instance_of_name(superClass, "SubClass"))
        self.assertTrue(is_instance_of_name(1, "int"))

    def test_params(self):
        self.assertEqual(["a"], func_params(SuperClass.__init__))
        self.assertEqual(["a", "b"], func_params(SubClass.__init__))
        self.assertEqual([], func_params(SubClass.square_b))
        self.assertEqual([], func_params(func1))
        self.assertEqual(["a", "b", "c", "d"], func_params(func2))


class SuperClass:
    def __init__(self, a):
        self.a = a


class SubClass(SuperClass):
    def __init__(self, a, b):
        super().__init__(a)
        self.b = b

    def square_b(self):
        return self.b**2


def func1():
    return 1


def func2(a, b, c=10, d=20):
    return a + b + c + d


if __name__ == "__main__":
    unittest.main()
