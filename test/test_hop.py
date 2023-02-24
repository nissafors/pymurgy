# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy.hop import Hop
from pymurgy.common import Stage, compute_cooling_coefficient


class TestHop(unittest.TestCase):
    def test_compute_boil_utilization(self):
        hop = Hop(time=6)
        expected = 0.0494752  # Pre-calculated
        actual = hop.compute_boil_utilization(1.055, 1.065)
        self.assertAlmostEqual(expected, actual, 6)

    def test_compute_post_boil_utilization(self):
        hop = Hop(time=6)
        expected = 0.0102109  # Pre-calculated
        k = compute_cooling_coefficient(20.0, 25.0, 20.0)
        actual = hop.compute_post_boil_utilization(1.055, 1.065, 20.0, 25.0, k)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu_boil(self):
        hop = Hop(stage=Stage.BOIL, g=56.7, time=6, aa=0.10)
        expected = 17.0317477  # Pre-calculated
        k = compute_cooling_coefficient(20.0, 25.0, 20.0)
        actual = hop.ibu(1.055, 1.065, 19.87, 20.0, 25.0, k)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu_ferment(self):
        hop = Hop(stage=Stage.FERMENT, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu(1.055, 1.065, 19.87, 20.0, 20.0, 25.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu_mash(self):
        hop = Hop(stage=Stage.MASH, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu(1.055, 1.065, 19.87, 20.0, 20.0, 25.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_serialize(self):
        hop = Hop(stage=Stage.FERMENT, name="Test hop", g=10.5, time=15, aa=0.05)
        d_0 = dict(hop)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("FERMENT", d["stage"])
        self.assertEqual("Test hop", d["name"])
        self.assertAlmostEqual(10.5, d["g"], 6)
        self.assertEqual(15, d["time"])
        self.assertAlmostEqual(0.05, d["aa"], 6)

    def test_from_dict(self):
        hop_0 = Hop(stage=Stage.FERMENT, name="Test hop", g=10.5, time=15, aa=0.05)
        j = json.dumps(dict(hop_0))
        d = json.loads(j)
        hop = Hop.from_dict(d)
        self.assertEqual(Stage.FERMENT, hop.stage)
        self.assertEqual("Test hop", hop.name)
        self.assertAlmostEqual(10.5, hop.g, 6)
        self.assertEqual(15, hop.time)
        self.assertAlmostEqual(0.05, hop.aa, 6)


if __name__ == "__main__":
    unittest.main()
