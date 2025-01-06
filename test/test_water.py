# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Stage, WaterProfile, SaltAdditions


class TestWaterProfile(unittest.TestCase):
    def setUp(self):
        self.water_profile = WaterProfile(
            ppm_calcium=7, ppm_sodium=2, ppm_magnesium=3, ppm_chloride=5, ppm_bicarbonate=25, ppm_sulfate=6
        )

    def test_init(self):
        self.assertEqual(7, self.water_profile.ppm_calcium)
        self.assertEqual(2, self.water_profile.ppm_sodium)
        self.assertEqual(3, self.water_profile.ppm_magnesium)
        self.assertEqual(5, self.water_profile.ppm_chloride)
        self.assertEqual(25, self.water_profile.ppm_bicarbonate)
        self.assertEqual(6, self.water_profile.ppm_sulfate)

    def test_alkalinity_as_cac03_to_ppm_hco0(self):
        alkalinity = 125
        expected_ppm_hco3 = 125 * 61 / 50
        actual_ppm_hco3 = self.water_profile.alkalinity_as_cac03_to_ppm_hco0(alkalinity)
        self.assertEqual(expected_ppm_hco3, actual_ppm_hco3)

    def test_ppm_hco0_to_alkalinity_as_cac03(self):
        ppm_hco3 = 150
        expected_alkalinity = 150 * 50 / 61
        actual_alkalinity = self.water_profile.ppm_hco0_to_alkalinity_as_cac03(ppm_hco3)
        self.assertEqual(expected_alkalinity, actual_alkalinity)

    def test_preset_pilsen(self):
        water_profile = WaterProfile.preset_pilsen()
        self.assertEqual(10, water_profile.ppm_calcium)
        self.assertEqual(3, water_profile.ppm_sodium)
        self.assertEqual(3, water_profile.ppm_magnesium)
        self.assertEqual(4, water_profile.ppm_chloride)
        self.assertEqual(3, water_profile.ppm_bicarbonate)
        self.assertEqual(4, water_profile.ppm_sulfate)

    def test_preset_dublin(self):
        water_profile = WaterProfile.preset_dublin()
        self.assertEqual(118, water_profile.ppm_calcium)
        self.assertEqual(12, water_profile.ppm_sodium)
        self.assertEqual(4, water_profile.ppm_magnesium)
        self.assertEqual(19, water_profile.ppm_chloride)
        self.assertEqual(319, water_profile.ppm_bicarbonate)
        self.assertEqual(54, water_profile.ppm_sulfate)

    def test_preset_dortmund(self):
        water_profile = WaterProfile.preset_dortmund()
        self.assertEqual(225, water_profile.ppm_calcium)
        self.assertEqual(60, water_profile.ppm_sodium)
        self.assertEqual(40, water_profile.ppm_magnesium)
        self.assertEqual(60, water_profile.ppm_chloride)
        self.assertEqual(220, water_profile.ppm_bicarbonate)
        self.assertEqual(120, water_profile.ppm_sulfate)

    def test_preset_vienna(self):
        water_profile = WaterProfile.preset_vienna()
        self.assertEqual(200, water_profile.ppm_calcium)
        self.assertEqual(8, water_profile.ppm_sodium)
        self.assertEqual(60, water_profile.ppm_magnesium)
        self.assertEqual(12, water_profile.ppm_chloride)
        self.assertEqual(120, water_profile.ppm_bicarbonate)
        self.assertEqual(125, water_profile.ppm_sulfate)

    def test_preset_munich(self):
        water_profile = WaterProfile.preset_munich()
        self.assertEqual(76, water_profile.ppm_calcium)
        self.assertEqual(5, water_profile.ppm_sodium)
        self.assertEqual(18, water_profile.ppm_magnesium)
        self.assertEqual(2, water_profile.ppm_chloride)
        self.assertEqual(152, water_profile.ppm_bicarbonate)
        self.assertEqual(10, water_profile.ppm_sulfate)

    def test_preset_london(self):
        water_profile = WaterProfile.preset_london()
        self.assertEqual(52, water_profile.ppm_calcium)
        self.assertEqual(86, water_profile.ppm_sodium)
        self.assertEqual(32, water_profile.ppm_magnesium)
        self.assertEqual(34, water_profile.ppm_chloride)
        self.assertEqual(104, water_profile.ppm_bicarbonate)
        self.assertEqual(32, water_profile.ppm_sulfate)

    def test_preset_edinburgh(self):
        water_profile = WaterProfile.preset_edinburgh()
        self.assertEqual(125, water_profile.ppm_calcium)
        self.assertEqual(55, water_profile.ppm_sodium)
        self.assertEqual(25, water_profile.ppm_magnesium)
        self.assertEqual(65, water_profile.ppm_chloride)
        self.assertEqual(225, water_profile.ppm_bicarbonate)
        self.assertEqual(140, water_profile.ppm_sulfate)

    def test_preset_burton(self):
        water_profile = WaterProfile.preset_burton()
        self.assertEqual(352, water_profile.ppm_calcium)
        self.assertEqual(54, water_profile.ppm_sodium)
        self.assertEqual(24, water_profile.ppm_magnesium)
        self.assertEqual(16, water_profile.ppm_chloride)
        self.assertEqual(320, water_profile.ppm_bicarbonate)
        self.assertEqual(820, water_profile.ppm_sulfate)

    def test_serialize(self):
        d_0 = dict(self.water_profile)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual(7, d["ppm_calcium"])
        self.assertEqual(2, d["ppm_sodium"])
        self.assertEqual(3, d["ppm_magnesium"])
        self.assertEqual(5, d["ppm_chloride"])
        self.assertEqual(25, d["ppm_bicarbonate"])
        self.assertEqual(6, d["ppm_sulfate"])

    def test_from_dict(self):
        water_profile_0 = self.water_profile
        j = json.dumps(dict(water_profile_0))
        d = json.loads(j)
        water_profile: WaterProfile = WaterProfile.from_dict(d)
        self.assertEqual(7, water_profile.ppm_calcium)
        self.assertEqual(2, water_profile.ppm_sodium)
        self.assertEqual(3, water_profile.ppm_magnesium)
        self.assertEqual(5, water_profile.ppm_chloride)
        self.assertEqual(25, water_profile.ppm_bicarbonate)
        self.assertEqual(6, water_profile.ppm_sulfate)


class TestSaltAdditions(unittest.TestCase):
    def setUp(self):
        self.litres_of_water = 5.0
        self.grams_of_salt = 2.5
        self.source = WaterProfile(
            ppm_calcium=7, ppm_sodium=2, ppm_magnesium=3, ppm_chloride=5, ppm_bicarbonate=25, ppm_sulfate=5
        )
        self.salts = SaltAdditions()

    def test_init(self):
        self.assertEqual(Stage.MASH, self.salts.stage)
        self.assertEqual(0, self.salts.g_caco3)
        self.assertEqual(0, self.salts.g_nahco3)
        self.assertEqual(0, self.salts.g_caso4)
        self.assertEqual(0, self.salts.g_cacl2)
        self.assertEqual(0, self.salts.g_mgso4)

    def test_profile(self):
        profile = self.salts.profile(source=self.source, volume=self.litres_of_water)
        # No salt additions means profile is equal to source profile
        self.assertEqual(self.source.ppm_calcium, profile.ppm_calcium)
        self.assertEqual(self.source.ppm_sodium, profile.ppm_sodium)
        self.assertEqual(self.source.ppm_magnesium, profile.ppm_magnesium)
        self.assertEqual(self.source.ppm_chloride, profile.ppm_chloride)
        self.assertEqual(self.source.ppm_bicarbonate, profile.ppm_bicarbonate)
        self.assertEqual(self.source.ppm_sulfate, profile.ppm_sulfate)
        # Same if volume is zero, even after salt additions
        self.salts.g_caco3 = self.grams_of_salt
        self.salts.g_nahco3 = self.grams_of_salt
        self.salts.g_caso4 = self.grams_of_salt
        self.salts.g_cacl2 = self.grams_of_salt
        self.salts.g_mgso4 = self.grams_of_salt
        profile = self.salts.profile(source=self.source, volume=0)
        self.assertEqual(self.source.ppm_calcium, profile.ppm_calcium)
        self.assertEqual(self.source.ppm_sodium, profile.ppm_sodium)
        self.assertEqual(self.source.ppm_magnesium, profile.ppm_magnesium)
        self.assertEqual(self.source.ppm_chloride, profile.ppm_chloride)
        self.assertEqual(self.source.ppm_bicarbonate, profile.ppm_bicarbonate)
        self.assertEqual(self.source.ppm_sulfate, profile.ppm_sulfate)
        # ValueError if volume is less than zero
        with self.assertRaises(ValueError):
            self.salts.profile(source=self.source, volume=-1)

    def test_set_g_caco3(self):
        self.salts.g_caco3 = self.grams_of_salt
        expected_ppm_ca = self.source.ppm_calcium + self._ppm_contrib(397.5)
        expected_ppm_hco3 = self.source.ppm_bicarbonate + self._ppm_contrib(598.1 * 61 / 30)
        profile = self.salts.profile(self.source, self.litres_of_water)
        self.assertAlmostEqual(expected_ppm_ca, profile.ppm_calcium, 6)
        self.assertAlmostEqual(expected_ppm_hco3, profile.ppm_bicarbonate, 6)

    def test_set_g_nahco3(self):
        self.salts.g_nahco3 = self.grams_of_salt
        expected_ppm_na = self.source.ppm_sodium + self._ppm_contrib(283.9)
        expected_ppm_hco3 = self.source.ppm_bicarbonate + self._ppm_contrib(723.0)
        profile = self.salts.profile(self.source, self.litres_of_water)
        self.assertAlmostEqual(expected_ppm_na, profile.ppm_sodium, 6)
        self.assertAlmostEqual(expected_ppm_hco3, profile.ppm_bicarbonate, 6)

    def test_set_g_caso4(self):
        self.salts.g_caso4 = self.grams_of_salt
        expected_ppm_ca = self.source.ppm_calcium + self._ppm_contrib(232.8)
        expected_ppm_so4 = self.source.ppm_sulfate + self._ppm_contrib(558.0)
        profile = self.salts.profile(self.source, self.litres_of_water)
        self.assertAlmostEqual(expected_ppm_ca, profile.ppm_calcium, 6)
        self.assertAlmostEqual(expected_ppm_so4, profile.ppm_sulfate, 6)

    def test_set_g_cacl2(self):
        self.salts.g_cacl2 = self.grams_of_salt
        expected_ppm_ca = self.source.ppm_calcium + self._ppm_contrib(272.5)
        expected_ppm_cl2 = self.source.ppm_chloride + self._ppm_contrib(480.7)
        profile = self.salts.profile(self.source, self.litres_of_water)
        self.assertAlmostEqual(expected_ppm_ca, profile.ppm_calcium, 6)
        self.assertAlmostEqual(expected_ppm_cl2, profile.ppm_chloride, 6)

    def test_set_g_mgso4(self):
        self.salts.g_mgso4 = self.grams_of_salt
        expected_ppm_mg = self.source.ppm_magnesium + self._ppm_contrib(98.4)
        expected_ppm_so4 = self.source.ppm_sulfate + self._ppm_contrib(389.9)
        profile = self.salts.profile(self.source, self.litres_of_water)
        self.assertAlmostEqual(expected_ppm_mg, profile.ppm_magnesium, 6)
        self.assertAlmostEqual(expected_ppm_so4, profile.ppm_sulfate, 6)

    def test_set_all_salts(self):
        expected_ppm_ca = self.source.ppm_calcium
        expected_ppm_na = self.source.ppm_sodium
        expected_ppm_mg = self.source.ppm_magnesium
        expected_ppm_cl2 = self.source.ppm_chloride
        expected_ppm_hco3 = self.source.ppm_bicarbonate
        expected_ppm_so4 = self.source.ppm_sulfate

        self.salts.g_caco3 = self.grams_of_salt
        expected_ppm_ca += self._ppm_contrib(397.5)
        expected_ppm_hco3 += self._ppm_contrib(598.1 * 61 / 30)

        self.salts.g_nahco3 = self.grams_of_salt
        expected_ppm_na += self._ppm_contrib(283.9)
        expected_ppm_hco3 += self._ppm_contrib(723.0)

        self.salts.g_caso4 = self.grams_of_salt
        expected_ppm_ca += self._ppm_contrib(232.8)
        expected_ppm_so4 += self._ppm_contrib(558.0)

        self.salts.g_cacl2 = self.grams_of_salt
        expected_ppm_ca += self._ppm_contrib(272.5)
        expected_ppm_cl2 += self._ppm_contrib(480.7)

        self.salts.g_mgso4 = self.grams_of_salt
        expected_ppm_mg += self._ppm_contrib(98.4)
        expected_ppm_so4 += self._ppm_contrib(389.9)

        profile = self.salts.profile(self.source, self.litres_of_water)

        self.assertAlmostEqual(expected_ppm_ca, profile.ppm_calcium, 6)
        self.assertAlmostEqual(expected_ppm_na, profile.ppm_sodium, 6)
        self.assertAlmostEqual(expected_ppm_mg, profile.ppm_magnesium, 6)
        self.assertAlmostEqual(expected_ppm_cl2, profile.ppm_chloride, 6)
        self.assertAlmostEqual(expected_ppm_hco3, profile.ppm_bicarbonate, 6)
        self.assertAlmostEqual(expected_ppm_so4, profile.ppm_sulfate, 6)

    def _ppm_contrib(self, conc_at_1g_per_liter: float):
        return conc_at_1g_per_liter * self.grams_of_salt / self.litres_of_water

    def test_serialize(self):
        salts = SaltAdditions(g_caco3=1, g_nahco3=2, g_caso4=3, g_cacl2=4, g_mgso4=5)
        d_0 = dict(salts)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("MASH", d["stage"])
        self.assertEqual(1, d["g_caco3"])
        self.assertEqual(2, d["g_nahco3"])
        self.assertEqual(3, d["g_caso4"])
        self.assertEqual(4, d["g_cacl2"])
        self.assertEqual(5, d["g_mgso4"])

    def test_from_dict(self):
        salts_0 = SaltAdditions(g_caco3=1, g_nahco3=2, g_caso4=3, g_cacl2=4, g_mgso4=5)
        j = json.dumps(dict(salts_0))
        d = json.loads(j)
        salts: SaltAdditions = SaltAdditions.from_dict(d)
        self.assertEqual(Stage.MASH, salts.stage)
        self.assertEqual(1, salts.g_caco3)
        self.assertEqual(2, salts.g_nahco3)
        self.assertEqual(3, salts.g_caso4)
        self.assertEqual(4, salts.g_cacl2)
        self.assertEqual(5, salts.g_mgso4)


if __name__ == "__main__":
    unittest.main()
