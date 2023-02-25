# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from pymurgy import abstract


class TestSerializable(unittest.TestCase):
    def test_iter(self):
        cut = abstract.Serializable()
        # Add a few attributes
        cut.attr_first = 1
        cut.attr_second = "two"
        # Assert that attributes can be serialized to dict
        expected = {"attr_first": 1, "attr_second": "two"}
        actual = dict(cut)
        self.assertDictEqual(expected, actual)

    def test_from_dict(self):
        # Assert that an instance can be created with from a dict. Use a derived class so we can test with more
        # attributes that "stage".
        ingr = SerializableSubClass.from_dict({"first": 1, "second": "two"})
        self.assertEqual(1, ingr.first)
        self.assertEqual("two", ingr.second)


class SerializableSubClass(abstract.Serializable):
    first: int = 0
    second: str = ""


if __name__ == "__main__":
    unittest.main()
