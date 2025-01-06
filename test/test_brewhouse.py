# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Brewhouse
from pymurgy.calc import cooling_coefficient
from pymurgy.ingredients.water import WaterProfile


class TestBrewhouse(unittest.TestCase):
    def test_init(self):
        brewhouse = Brewhouse(boil_off_rate=0.15, temp_approach=10, temp_target=20, cool_time_boil_to_target=45)
        self.assertEqual(0.15, brewhouse.boil_off_rate)
        self.assertEqual(10, brewhouse.temp_approach)
        self.assertEqual(20, brewhouse.temp_target)
        self.assertEqual(45, brewhouse.cool_time_boil_to_target)

    def test_cooling_coefficient(self):
        brewhouse = Brewhouse(boil_off_rate=0.15, temp_approach=10, temp_target=20, cool_time_boil_to_target=45)
        expected = cooling_coefficient(10, 20, 45, 100)
        actual = brewhouse.cooling_coefficient()
        self.assertAlmostEqual(expected, actual, 6)

    def test_serialize(self):
        water_profile = WaterProfile.preset_edinburgh()
        brewhouse = Brewhouse(
            boil_off_rate=0.15,
            temp_approach=10,
            temp_target=20,
            cool_time_boil_to_target=45,
            water_profile=water_profile,
        )
        d_0 = dict(brewhouse)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual(0.15, d["boil_off_rate"])
        self.assertEqual(10, d["temp_approach"])
        self.assertEqual(20, d["temp_target"])
        self.assertEqual(45, d["cool_time_boil_to_target"])
        self.assertEqual(water_profile.ppm_calcium, d["water_profile"]["ppm_calcium"])
        self.assertEqual(water_profile.ppm_sodium, d["water_profile"]["ppm_sodium"])
        self.assertEqual(water_profile.ppm_magnesium, d["water_profile"]["ppm_magnesium"])
        self.assertEqual(water_profile.ppm_chloride, d["water_profile"]["ppm_chloride"])
        self.assertEqual(water_profile.ppm_bicarbonate, d["water_profile"]["ppm_bicarbonate"])
        self.assertEqual(water_profile.ppm_sulfate, d["water_profile"]["ppm_sulfate"])

    def test_from_dict(self):
        water_profile = WaterProfile.preset_edinburgh()
        brewhouse_0 = Brewhouse(
            boil_off_rate=0.15,
            temp_approach=10,
            temp_target=20,
            cool_time_boil_to_target=45,
            water_profile=water_profile,
        )
        j = json.dumps(dict(brewhouse_0))
        d = json.loads(j)
        brewhouse: Brewhouse = Brewhouse.from_dict(d)
        self.assertEqual(0.15, brewhouse.boil_off_rate)
        self.assertEqual(10, brewhouse.temp_approach)
        self.assertEqual(20, brewhouse.temp_target)
        self.assertEqual(45, brewhouse.cool_time_boil_to_target)
        self.assertEqual(water_profile.ppm_calcium, brewhouse.water_profile.ppm_calcium)
        self.assertEqual(water_profile.ppm_sodium, brewhouse.water_profile.ppm_sodium)
        self.assertEqual(water_profile.ppm_magnesium, brewhouse.water_profile.ppm_magnesium)
        self.assertEqual(water_profile.ppm_chloride, brewhouse.water_profile.ppm_chloride)
        self.assertEqual(water_profile.ppm_bicarbonate, brewhouse.water_profile.ppm_bicarbonate)
        self.assertEqual(water_profile.ppm_sulfate, brewhouse.water_profile.ppm_sulfate)


if __name__ == "__main__":
    unittest.main()
