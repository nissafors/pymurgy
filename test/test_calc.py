# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest
from pymurgy import calc


class TestCalc(unittest.TestCase):
    def test_celsius_to_kelvin(self):
        expected = 293.15
        actual = calc.celsius_to_kelvin(20)
        self.assertAlmostEqual(expected, actual, 6)

    def test_kelvin_to_celsius(self):
        expected = 26.85
        actual = calc.kelvin_to_celsius(300)
        self.assertAlmostEqual(expected, actual, 6)

    def test_celsius_to_fahrenheit(self):
        # 10 deg C
        expected = 50.0  # Pre-calculated
        actual = calc.celsius_to_fahrenheit(10.0)
        self.assertEqual(expected, actual)

    def test_fahrenheit_to_celsius(self):
        # 50 deg F
        expected = 10.0
        actual = calc.fahrenheit_to_celsius(50.0)
        self.assertEqual(expected, actual)

    def test_to_plato(self):
        expected = 11.89749826  # Pre-calculated
        actual = calc.to_plato(1.048)
        self.assertAlmostEqual(expected, actual, 6)
        expected = 17.03415942  # Pre-calculated
        actual = calc.to_plato(1.070)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_psi(self):
        # 0.7 bar
        expected = 10.1526416  # Pre-calculated
        actual = calc.to_psi(0.7)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_psi(self):
        # 8 psi
        expected = 0.5515808  # Pre-calculated
        actual = calc.to_bar(8.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_gallons(self):
        # 20 litres
        expected = 5.2834410  # Pre-calculated
        actual = calc.to_gallons(20.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_to_litres(self):
        # 5 gallons
        expected = 18.927059  # Pre-calculated
        actual = calc.to_litres(5.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_cooling_coefficient(self):
        expected = 0.1386294  # Pre-calculated
        actual = calc.cooling_coefficient(20.0, 25.0, 20.0, 100.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_cool_time(self):
        k = 0.13862943611198905  # Pre-calculated
        expected = 20.0
        actual = calc.cool_time(20.0, 25.0, k, 100.0)
        self.assertAlmostEqual(expected, actual, 6)


if __name__ == "__main__":
    unittest.main()
