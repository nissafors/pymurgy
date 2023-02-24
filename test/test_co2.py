# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy.co2 import CO2
from pymurgy.common import Stage
from pymurgy.extract import Fermentable


class TestCO2(unittest.TestCase):
    def test_init(self):
        co2 = CO2(volumes=2.5)
        self.assertEqual(2.5, co2.volumes)
        self.assertEqual(Stage.CONDITION, co2.stage)

    def test_force_carbonation_pressure(self):
        # Expected values from online calculator: https://www.brewersfriend.com/keg-carbonation-calculator/
        # Brewer's friend's calculator rounds to 2 decimals.
        # 2 volumes, 5C -> 0.50 bar
        co2 = CO2(volumes=2.0)
        expected = 0.50
        actual = co2.force_carbonation_pressure(5.0)
        self.assertAlmostEqual(expected, actual, 2)
        # 2.5 volumes, 1c -> 0.63 bar
        co2 = CO2(volumes=2.5)
        expected = 0.63
        actual = co2.force_carbonation_pressure(1.0)
        self.assertAlmostEqual(expected, actual, 2)
        # 1.5 volumes, 10C -> 0.34
        co2 = CO2(volumes=1.5)
        expected = 0.34
        actual = co2.force_carbonation_pressure(10.0)
        self.assertAlmostEqual(expected, actual, 2)

    def test_priming(self):
        # Expected values from online calculator: https://www.brewersfriend.com/beer-priming-calculator/
        # Brewer's friend's calculator rounds to 1 decimal.
        # 2 volumes, 0.33l/package, 15C, hwe 384 -> 1.3g
        co2 = CO2(volumes=2.0)
        expected = 1.3
        actual = co2.priming(volume=0.33, temp=15)
        self.assertAlmostEqual(expected, actual, 1)
        # 2.5 volumes, 19l/package, 20C, hwe 317 -> 168.3g
        co2 = CO2(volumes=2.5)
        expected = 136.8
        actual = co2.priming(
            volume=19, temp=20, hwe=Fermentable.CORN_SUGAR.hwe, fermemtability=Fermentable.CORN_SUGAR.fermentability
        )
        self.assertAlmostEqual(expected, actual, 1)
        # 2.5 volumes, 19l/package, 20C, hwe 317 -> 168.3g
        co2 = CO2(volumes=2.5)
        expected = 159.45  # I'm starting totrust this calculator more than Brewer's friend's which said 168.3.
        actual = co2.priming(
            volume=19, temp=20, hwe=Fermentable.HONEY.hwe, fermemtability=Fermentable.HONEY.fermentability
        )
        self.assertAlmostEqual(expected, actual, 2)

    def test_serialize(self):
        co2 = CO2(volumes=2.5)
        d_0 = dict(co2)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("CONDITION", d["stage"])
        self.assertEqual(2.5, d["volumes"])

    def test_from_dict(self):
        co2_0 = CO2(volumes=2.5)
        j = json.dumps(dict(co2_0))
        d = json.loads(j)
        co2: CO2 = CO2.from_dict(d)
        self.assertEqual(Stage.CONDITION, co2.stage)
        self.assertEqual(2.5, co2.volumes)


if __name__ == "__main__":
    unittest.main()
