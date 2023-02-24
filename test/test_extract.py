# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy.extract import Extract
from pymurgy.common import Stage


class TestExtract(unittest.TestCase):
    def test_hwe(self):
        extract = Extract(max_hwe=300)
        expected = 300 * 0.75
        actual = extract.hwe(0.75)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_mashable_mash(self):
        # Most common case
        extract = Extract(kg=2.0, max_hwe=300, mashable=True, stage=Stage.MASH)
        expected = 1.048  # Pre-calculated
        actual = extract.sg(volume=10.0, efficiency=0.8)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_mashable_boil(self):
        # Steeping grain
        extract = Extract(kg=2.0, max_hwe=300, mashable=True, stage=Stage.BOIL)
        expected = 1.015  # Pre-calculated
        actual = extract.sg(volume=10.0, efficiency=0.8, steeping_efficiency=0.25)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_mashable_ferment(self):
        # Erratic brewer, should not add to gravity
        extract = Extract(kg=2.0, max_hwe=300, mashable=True, stage=Stage.FERMENT)
        expected = 1.0
        actual = extract.sg(volume=10.0, efficiency=0.8)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_non_mashable_boil(self):
        # LME, DME or sugar addition to boil
        extract = Extract(kg=0.5, max_hwe=380, mashable=False, stage=Stage.BOIL, fermentability=1.0)
        expected = 1.019  # Pre-calculated
        actual = extract.sg(volume=10.0, efficiency=0.8)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_non_mashable_ferment(self):
        # LME, DME or sugar addition to fermenter
        extract = Extract(kg=0.5, max_hwe=380, mashable=False, stage=Stage.FERMENT, fermentability=1.0)
        expected = 1.019  # Pre-calculated
        actual = extract.sg(volume=10.0, efficiency=0.8, include_post_boil=True)
        self.assertAlmostEqual(expected, actual, 6)

    def test_sg_non_mashable_ferment_exclude_fermenter_additions(self):
        # LME, DME or sugar addition to fermenter, but exclude additions to fermenter. This option can be used for post
        # boil gravity calculations.
        extract = Extract(kg=0.5, max_hwe=380, mashable=False, stage=Stage.FERMENT, fermentability=1.0)
        expected = 1.0
        actual = extract.sg(volume=10.0, efficiency=0.8, include_post_boil=False)
        self.assertAlmostEqual(expected, actual, 6)

    def test_emcu(self):
        # Color
        extract = Extract(kg=0.5, deg_ebc=25)
        expected = 1.25  # Pre-calculated
        actual = extract.emcu(volume=10.0)
        self.assertAlmostEqual(expected, actual, 6)

    def test_percent_extract_to_hwe(self):
        # 80% of 384 (HWE for sucrose) = 307.2
        expected = 307.2
        actual = Extract.percent_extract_to_hwe(80)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ppg_to_hwe(self):
        # Conversion factor: (gallons/l) / (pounds/kg)
        # 46 * 8.3454044 = 383.8886043
        expected = 383.8886043
        actual = Extract.ppg_to_hwe(46)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ppg_to_hwe(self):
        # See above ^
        expected = 46.0
        actual = Extract.hwe_to_ppg(383.8886043)
        self.assertAlmostEqual(expected, actual, 6)

    def test_serialize(self):
        extract = Extract(
            stage=Stage.MASH,
            name="Test extract",
            description="An extract",
            kg=0.5,
            max_hwe=380,
            deg_ebc=25.0,
            fermentability=None,
            mashable=False,
        )
        d_0 = dict(extract)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("MASH", d["stage"])
        self.assertEqual("Test extract", d["name"])
        self.assertEqual("An extract", d["description"])
        self.assertAlmostEqual(0.5, d["kg"], 6)
        self.assertEqual(380, d["max_hwe"])
        self.assertAlmostEqual(25.0, d["deg_ebc"], 6)
        self.assertEqual(None, d["fermentability"])
        self.assertFalse(d["mashable"])
        self.assertEqual(8, len(d))

    def test_from_dict(self):
        extract_0 = Extract(
            stage=Stage.MASH,
            name="Test extract",
            description="An extract",
            kg=0.5,
            max_hwe=380,
            deg_ebc=25.0,
            fermentability=None,
            mashable=False,
        )
        j = json.dumps(dict(extract_0))
        d = json.loads(j)
        extract: Extract = Extract.from_dict(d)
        self.assertEqual(Stage.MASH, extract.stage)
        self.assertEqual("Test extract", extract.name)
        self.assertEqual("An extract", extract.description)
        self.assertAlmostEqual(0.5, extract.kg, 6)
        self.assertEqual(380, extract.max_hwe)
        self.assertAlmostEqual(25.0, extract.deg_ebc, 6)
        self.assertEqual(None, extract.fermentability)
        self.assertFalse(extract.mashable)


if __name__ == "__main__":
    unittest.main()
