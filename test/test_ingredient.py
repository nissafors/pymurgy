# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from dataclasses import dataclass
from pymurgy.ingredients.ingredient import Ingredient
from pymurgy import Stage


class TestIngredient(unittest.TestCase):
    def test_iter(self):
        cut = Ingredient()
        # Add a few attributes
        cut.attr_first = 1
        cut.attr_second = "two"
        # Assert that attributes can be serialized to dict
        expected = {"stage": "BOIL", "attr_first": 1, "attr_second": "two"}
        actual = dict(cut)
        self.assertDictEqual(expected, actual)

    def test_from_dict(self):
        # Assert that an instance can be created with from a dict. Use a derived class so we can test with more
        # attributes that "stage".
        ingr = IngredientBaseSubClass.from_dict({"stage": "MASH", "first": 1, "second": "two"})
        self.assertEqual(Stage.MASH, ingr.stage)
        self.assertEqual(1, ingr.first)
        self.assertEqual("two", ingr.second)


@dataclass
class IngredientBaseSubClass(Ingredient):
    first: int = 0
    second: str = ""


if __name__ == "__main__":
    unittest.main()
