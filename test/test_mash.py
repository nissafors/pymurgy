# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Mash, Temperature


class TestMash(unittest.TestCase):
    def setUp(self):
        steps = [Temperature(temp_init=65, temp_final=65, time=60), Temperature(temp_init=75, temp_final=75, time=10)]
        self.mash = Mash(
            instructions="Test instructions.", efficiency=0.8, steps=steps, absorption=1.2, liqour_to_grist_ratio=3.0
        )

    def test_init(self):
        self.assertEqual("Test instructions.", self.mash.instructions)
        self.assertEqual(0.8, self.mash.efficiency)
        self.assertEqual(65, self.mash.steps[0].temp_init)
        self.assertEqual(65, self.mash.steps[0].temp_final)
        self.assertEqual(60, self.mash.steps[0].time)
        self.assertEqual(75, self.mash.steps[1].temp_init)
        self.assertEqual(75, self.mash.steps[1].temp_final)
        self.assertEqual(10, self.mash.steps[1].time)
        self.assertEqual(3.0, self.mash.liqour_to_grist_ratio)
        self.assertEqual(1.2, self.mash.absorption)
        self.assertEqual(1.722, self.mash.grist_heat_capacity)
        self.assertEqual(0.67, self.mash.displacement)

    def test_strike_volume(self):
        # liqour to grist ratio = liters of water / kg's of grains
        # Let kg's of grain = 4.0
        # 2.5 = X / 4.0 -> X = 10.0
        self.mash.liqour_to_grist_ratio = 2.5
        self.assertEqual(10.0, self.mash.strike_volume(4.0))
        # 3.2 = X / 4.0 -> X = 12.8
        self.mash.liqour_to_grist_ratio = 3.2
        self.assertEqual(12.8, self.mash.strike_volume(4.0))

    def test_total_volume(self):
        # v_wort = v_total - absorption * m_grain
        # v_sparge is unknown and v_total = v_strike + v_sparge
        # Let m_grain = 4 and v_wort = 20
        v_wort = 20
        m_grain = 4
        expected = v_wort + self.mash.absorption * m_grain
        actual = self.mash.total_volume(m_grain, v_wort)
        self.assertEqual(expected, actual)

    def test_strike_temp(self):
        # Let kg's of grain = 4.0, room temperature = 20.
        # Using default grain heat capacity the formula becomes (as in How to brew):
        #   strike_temp = (t_target - t_grist) * 0.41 * kg_grist / vol_strike + t_target
        kg_grain = 4
        t_room = 20
        t_target = self.mash.steps[0].temp_init
        vol_strike = self.mash.strike_volume(kg_grain)
        expected = (t_target - t_room) * 0.41 * kg_grain / vol_strike + t_target
        actual = self.mash.strike_temp(t_room, kg_grain, vol_strike)
        self.assertEqual(expected, actual)

    def test_infusion_volume(self):
        steps = [
            Temperature(temp_init=40, temp_final=40, time=20),
            Temperature(temp_init=45, temp_final=45, time=10),
            Temperature(temp_init=55, temp_final=55, time=20),
            Temperature(temp_init=65, temp_final=65, time=40),
            Temperature(temp_init=77, temp_final=77, time=10),
        ]
        self.mash.steps = steps
        # Let kg's of grain = 4.0.
        # Using default grain heat capacity the formula becomes (as in How to brew):
        #   vol_inf = (t_target - t_init) * (0.41 * kg_grist + cur_vol) / (t_water - t_target)
        kg_grain = 4
        strike_vol = self.mash.strike_volume(kg_grain)
        # Step 1
        t_init = self.mash.steps[0].temp_final
        t_target = self.mash.steps[1].temp_init
        cur_vol = strike_vol
        expected = (t_target - t_init) * (0.41 * kg_grain + cur_vol) / (100 - t_target)
        actual = self.mash.infusion_volume(1, kg_grain, strike_vol)
        self.assertEqual(expected, actual)
        # Step 2
        t_init = self.mash.steps[1].temp_final
        t_target = self.mash.steps[2].temp_init
        cur_vol += expected  # Volume after initial strike + infusion volume from step 1
        expected = (t_target - t_init) * (0.41 * kg_grain + cur_vol) / (100 - t_target)
        actual = self.mash.infusion_volume(2, kg_grain, strike_vol)
        self.assertEqual(expected, actual)
        # Step 3
        t_init = self.mash.steps[2].temp_final
        t_target = self.mash.steps[3].temp_init
        cur_vol += expected
        expected = (t_target - t_init) * (0.41 * kg_grain + cur_vol) / (100 - t_target)
        actual = self.mash.infusion_volume(3, kg_grain, strike_vol)
        self.assertEqual(expected, actual)
        # Step 4
        t_init = self.mash.steps[3].temp_final
        t_target = self.mash.steps[4].temp_init
        cur_vol += expected
        expected = (t_target - t_init) * (0.41 * kg_grain + cur_vol) / (100 - t_target)
        actual = self.mash.infusion_volume(4, kg_grain, strike_vol)
        self.assertEqual(expected, actual)
        # Step 0 raises ValueError
        with self.assertRaises(ValueError):
            self.mash.infusion_volume(0, kg_grain, strike_vol)
        # Step > 4 raises ValueError
        with self.assertRaises(ValueError):
            self.mash.infusion_volume(5, kg_grain, strike_vol)
        # Step 3 overriding mash_temp and mash_volume and lower infusion water temp
        t_init = 52
        t_target = self.mash.steps[3].temp_init
        cur_vol = 18
        expected = (t_target - t_init) * (0.41 * kg_grain + cur_vol) / (95 - t_target)
        actual = self.mash.infusion_volume(
            3, kg_grain, strike_vol, water_temp=95, mash_temp=t_init, liqour_volume=cur_vol
        )
        self.assertEqual(expected, actual)

    def test_adjust_volume(self):
        m_grist = 4
        t_init = 62
        t_target = 65
        v_mash = 15
        t_water = 95
        # Same formula as in the above test
        expected = (t_target - t_init) * (0.41 * m_grist + v_mash) / (t_water - t_target)
        actual = self.mash.adjustment_volume(m_grist, t_init, t_target, v_mash, t_water)
        self.assertEqual(expected, actual)

    def test_liqour_volume(self):
        # Let m_grain = 4 and v_mash = 15
        expected = 15 - 4 * 0.67
        actual = self.mash.liqour_volume(4, 15)
        self.assertEqual(expected, actual)

    def test_required_space(self):
        # Let m_grain = 4 and v_water = 12
        # Verified with the "Can I mash it" calculator at https://www.rackers.org/calcs.shtml
        expected = 12 + 4 * 0.67
        actual = self.mash.required_space(4, 12)
        self.assertEqual(expected, actual)

    def test_serialize(self):
        d_0 = dict(self.mash)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("Test instructions.", d["instructions"])
        self.assertEqual(0.8, d["efficiency"])
        self.assertEqual(65, d["steps"][0]["temp_init"])
        self.assertEqual(65, d["steps"][0]["temp_final"])
        self.assertEqual(60, d["steps"][0]["time"])
        self.assertEqual(75, d["steps"][1]["temp_init"])
        self.assertEqual(75, d["steps"][1]["temp_final"])
        self.assertEqual(10, d["steps"][1]["time"])
        self.assertEqual(3.0, d["liqour_to_grist_ratio"])
        self.assertEqual(1.2, d["absorption"])
        self.assertEqual(1.722, d["grist_heat_capacity"])
        self.assertEqual(0.67, d["displacement"])

    def test_from_dict(self):
        mash_0 = self.mash
        j = json.dumps(dict(mash_0))
        d = json.loads(j)
        mash: Mash = Mash.from_dict(d)
        self.assertEqual("Test instructions.", mash.instructions)
        self.assertEqual(0.8, self.mash.efficiency)
        self.assertEqual(65, mash.steps[0].temp_init)
        self.assertEqual(65, mash.steps[0].temp_final)
        self.assertEqual(60, mash.steps[0].time)
        self.assertEqual(75, mash.steps[1].temp_init)
        self.assertEqual(75, mash.steps[1].temp_final)
        self.assertEqual(10, mash.steps[1].time)
        self.assertEqual(3.0, mash.liqour_to_grist_ratio)
        self.assertEqual(1.2, self.mash.absorption)
        self.assertEqual(1.722, mash.grist_heat_capacity)
        self.assertEqual(0.67, mash.displacement)


if __name__ == "__main__":
    unittest.main()
