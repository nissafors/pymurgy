# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from pymurgy import BeerStyle, BeerFamily


class TestBeerStyle(unittest.TestCase):
    def test_compare(self):
        self.assertEqual(BeerStyle.PALE_LAGER, BeerStyle.PALE_LAGER)
        self.assertNotEqual(BeerStyle.PALE_ALE, BeerStyle.PALE_LAGER)

    def test_family(self):
        expected = BeerFamily.ALE
        style = BeerStyle.STOUT
        actual = style.family
        self.assertEqual(expected, actual)
        self.assertNotEqual(expected, style)
        expected = BeerFamily.LAGER
        actual = BeerStyle.BOCK.family
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
