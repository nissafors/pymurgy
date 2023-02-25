# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Brewhouse
from pymurgy.calc import cooling_coefficient


class TestYeast(unittest.TestCase):
    def test_init(self):
        brewhouse = Brewhouse(
            boil_off_rate=0.15, efficiency=0.8, temp_approach=10, temp_target=20, cool_time_boil_to_target=45
        )
        self.assertEqual(0.15, brewhouse.boil_off_rate)
        self.assertEqual(0.8, brewhouse.efficiency)
        self.assertEqual(10, brewhouse.temp_approach)
        self.assertEqual(20, brewhouse.temp_target)
        self.assertEqual(45, brewhouse.cool_time_boil_to_target)

    def test_cooling_coefficient(self):
        brewhouse = Brewhouse(
            boil_off_rate=0.15, efficiency=0.8, temp_approach=10, temp_target=20, cool_time_boil_to_target=45
        )
        expected = cooling_coefficient(10, 20, 45, 100)
        actual = brewhouse.cooling_coefficient()
        self.assertAlmostEqual(expected, actual, 6)

    def test_serialize(self):
        brewhouse = Brewhouse(
            boil_off_rate=0.15, efficiency=0.8, temp_approach=10, temp_target=20, cool_time_boil_to_target=45
        )
        d_0 = dict(brewhouse)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual(0.15, d["boil_off_rate"])
        self.assertEqual(0.8, d["efficiency"])
        self.assertEqual(10, d["temp_approach"])
        self.assertEqual(20, d["temp_target"])
        self.assertEqual(45, d["cool_time_boil_to_target"])

    def test_from_dict(self):
        brewhouse_0 = Brewhouse(
            boil_off_rate=0.15, efficiency=0.8, temp_approach=10, temp_target=20, cool_time_boil_to_target=45
        )
        j = json.dumps(dict(brewhouse_0))
        d = json.loads(j)
        brewhouse: Brewhouse = Brewhouse.from_dict(d)
        self.assertEqual(0.15, brewhouse.boil_off_rate)
        self.assertEqual(0.8, brewhouse.efficiency)
        self.assertEqual(10, brewhouse.temp_approach)
        self.assertEqual(20, brewhouse.temp_target)
        self.assertEqual(45, brewhouse.cool_time_boil_to_target)


if __name__ == "__main__":
    unittest.main()
