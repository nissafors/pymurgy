# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from dataclasses import dataclass
from pymurgy import common


class TestBeerStyle(unittest.TestCase):
    def test_compare(self):
        self.assertEqual(common.BeerStyle.PALE_LAGER, common.BeerStyle.PALE_LAGER)
        self.assertNotEqual(common.BeerStyle.PALE_ALE, common.BeerStyle.PALE_LAGER)

    def test_family(self):
        expected = common.BeerFamily.ALE
        style = common.BeerStyle.STOUT
        actual = style.family
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected, style)
        expected = common.BeerFamily.LAGER
        actual = common.BeerStyle.BOCK.family
        self.assertEqual(expected, actual)


class TestSerializable(unittest.TestCase):
    def test_iter(self):
        cut = common.Serializable()
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


class TestIngredient(unittest.TestCase):
    def test_iter(self):
        cut = common.Ingredient()
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
        self.assertEqual(common.Stage.MASH, ingr.stage)
        self.assertEqual(1, ingr.first)
        self.assertEqual("two", ingr.second)


class TestFunctions(unittest.TestCase):
    def test_to_kelvin(self):
        expected = 293.15
        actual = common.to_kelvin(20)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_fahrenheit(self):
        # 10 deg C
        expected = 50.0  # Pre-calculated
        actual = common.to_fahrenheit(10.0)
        self.assertEqual(expected, actual)

    def test_to_plato(self):
        expected = 11.89749826  # Pre-calculated
        actual = common.to_plato(1.048)
        self.assertAlmostEqual(expected, actual, 6)
        expected = 17.03415942  # Pre-calculated
        actual = common.to_plato(1.070)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_to_psi(self):
        # 0.7 bar
        expected = 10.1526416  # Pre-calculated
        actual = common.to_psi(0.7)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_to_psi(self):
        # 8 psi
        expected = 0.5515808  # Pre-calculated
        actual = common.to_bar(8.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_gallons(self):
        # 20 litres
        expected = 5.2834410  # Pre-calculated
        actual = common.to_gallons(20.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_litres(self):
        # 5 gallons
        expected = 18.927059  # Pre-calculated
        actual = common.to_litres(5.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_compute_cooling_coefficient(self):
        expected = 0.1386294  # Pre-calculated
        actual = common.compute_cooling_coefficient(20.0, 25.0, 20.0, 100.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_compute_cool_time(self):
        k = 0.13862943611198905  # Pre-calculated
        expected = 20.0
        actual = common.compute_cool_time(20.0, 25.0, k, 100.0)
        self.assertAlmostEqual(expected, actual, 6)


class SerializableSubClass(common.Serializable):
    first: int = 0
    second: str = ""


@dataclass
class IngredientBaseSubClass(common.Ingredient):
    first: int = 0
    second: str = ""


if __name__ == "__main__":
    unittest.main()
