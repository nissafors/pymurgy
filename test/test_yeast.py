# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Yeast, Stage, BeerStyle
from pymurgy.calc import to_plato


class TestYeast(unittest.TestCase):
    def test_init(self):
        yeast = Yeast(name="Test yeast", attenuation=0.7)
        self.assertEqual("Test yeast", yeast.name)
        self.assertAlmostEqual(0.7, yeast.attenuation, 6)
        self.assertEqual(Stage.FERMENT, Yeast.stage)

    def test_cells_to_pitch(self):
        # Rule of thumb: 1 million cells per ml of wort per degree plato.
        # Then factor in beer style and gravity:
        # 0.75: ale, 1.0: high gravity ale, 1.5: lager, 2.0: high gravity lager.
        # High gravity is defined as > 1.060
        # Normal ale, 20 litres, og: 1.060:
        expected = int(round(1000000 * 0.75 * 20000 * to_plato(1.060)))
        actual = Yeast.cells_to_pitch(20, BeerStyle.ALE, 1.060)
        self.assertEqual(expected, actual)
        # Normal lager, 20 litres, og: 1.060:
        expected = int(round(1000000 * 1.5 * 20000 * to_plato(1.060)))
        actual = Yeast.cells_to_pitch(20, BeerStyle.LAGER, 1.060)
        self.assertEqual(expected, actual)
        # High gravity ale, 20 litres, og: 1.061:
        expected = int(round(1000000 * 1.0 * 20000 * to_plato(1.061)))
        actual = Yeast.cells_to_pitch(20, BeerStyle.ALE, 1.061)
        self.assertEqual(expected, actual)
        # High gravity lager, 20 litres, og: 1.061:
        expected = int(round(1000000 * 2.0 * 20000 * to_plato(1.061)))
        actual = Yeast.cells_to_pitch(20, BeerStyle.LAGER, 1.061)
        self.assertEqual(expected, actual)
        # Custom pitch rate
        expected = int(round(1000000 * 0.8 * 20000 * to_plato(1.061)))
        actual = Yeast.cells_to_pitch(20, None, 1.061, 0.8)
        self.assertEqual(expected, actual)

    def test_grams_of_dry_yeast(self):
        # I want to pitch 50 billion cells, I have 20 billion cells per gram (default). I need 2.5 grams.
        expected = 2.5
        actual = Yeast.grams_of_dry_yeast(50000000000)
        self.assertAlmostEqual(expected, actual, 6)
        # I want to pitch 50 billion cells, I have 10 billion cells per gram (default). I need 5 grams.
        expected = 5.0
        actual = Yeast.grams_of_dry_yeast(50000000000, 10)
        self.assertAlmostEqual(expected, actual, 6)

    def test_litres_of_slurry(self):
        # I want to pitch 150 billion cells, I have 1 billion cells per ml (default). That's 1000 billion cells per
        # litre. I need 0.15 litres of slurry.
        expected = 0.15
        actual = Yeast.litres_of_slurry(150000000000)
        self.assertAlmostEqual(expected, actual, 6)

    def test_packets_of_liquid_yeast(self):
        # I want to pitch 150 billion cells, I have 100 billion cells per packages (default).
        # Viability is 96% on day 0. I need ~1.6 packages.
        viability = 0.96 * 0.785**0
        expected = 150 / (100 * viability)
        actual = Yeast.packets_of_liquid_yeast(150000000000, 0)
        self.assertAlmostEqual(expected, actual, 6)
        # I want to pitch 150 billion cells, I have 100 billion cells per packages (default).
        # Viability is ~75% after 1 month. I need ~2 packages.
        viability = 0.96 * 0.785**1
        expected = 150 / (100 * viability)
        actual = Yeast.packets_of_liquid_yeast(150000000000, 30)
        self.assertAlmostEqual(expected, actual, 6)
        # I want to pitch 150 billion cells, I have 100 billion cells per packages (default).
        # Viability is ~59% after 2 months. I need 2.5 packages.
        viability = 0.96 * 0.785**2
        expected = 150 / (100 * viability)
        actual = Yeast.packets_of_liquid_yeast(150000000000, 60)
        self.assertAlmostEqual(expected, actual, 6)

    def test_cells_in_liquid_yeast_package(self):
        # On manufacturing day viability is 96%
        viability = 0.96 * 0.785**0
        expected = int(round(100000000000 * viability))
        actual = Yeast.cells_in_liquid_yeast_package(0)
        self.assertEqual(expected, actual)
        # Day two viability is ~95%
        viability = 0.96 * 0.785 ** (1 / 30)
        expected = int(round(100000000000 * viability))
        actual = Yeast.cells_in_liquid_yeast_package(1)
        self.assertEqual(expected, actual)
        # After one month viability is ~75%
        viability = 0.96 * 0.785**1
        expected = int(round(100000000000 * viability))
        actual = Yeast.cells_in_liquid_yeast_package(30)
        self.assertEqual(expected, actual)

    def test_starter(self):
        # Some known values from table in yeast book
        # Inoculation rate: 200M/ml
        expected = 112000000000
        actual = Yeast.starter(0.5, 100)
        self.assertEqual(expected, actual)
        expected = 112000000000 * 3
        actual = Yeast.starter(0.5 * 3, 100 * 3)
        self.assertEqual(expected, actual)
        # Inoculation rate: 50M/ml
        expected = 205000000000
        actual = Yeast.starter(2, 100)
        self.assertEqual(expected, actual)
        expected = 205000000000 * 5
        actual = Yeast.starter(2 * 5, 100 * 5)
        self.assertEqual(expected, actual)
        # Inoculation rate: 5M/ml
        expected = 600000000000
        actual = Yeast.starter(20, 100)
        self.assertEqual(expected, actual)
        expected = 600000000000 * 2.5
        actual = Yeast.starter(20 * 2.5, 100 * 2.5)
        self.assertEqual(expected, actual)
        # Inoculation rates above 400 results in no growth in the model
        expected = 100000000000
        actual = Yeast.starter(0.25, 100)
        self.assertEqual(expected, actual)
        actual = Yeast.starter(0.2, 100)
        self.assertEqual(expected, actual)
        # Inoculation rate 100 / (1 / 3) = 300 interpolated between 100 / 0.25 = 400 and 100 / 0.5 = 200 in the table.
        # Should result in half way between 1 and 1.12 billion cells
        expected = 106000000000
        actual = Yeast.starter(1 / 3, 100)
        self.assertEqual(expected, actual)
        # Inoculation rates below 5 results in a growth factor of 6 regardless.
        expected = 600000000000
        actual = Yeast.starter(21, 100)
        self.assertEqual(expected, actual)
        actual = Yeast.starter(30, 100)
        self.assertEqual(expected, actual)

    def test_serialize(self):
        yeast = Yeast(name="Test yeast", description="A made up yeast", attenuation=0.7)
        d_0 = dict(yeast)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("FERMENT", d["stage"])
        self.assertEqual("Test yeast", d["name"])
        self.assertEqual("A made up yeast", d["description"])
        self.assertAlmostEqual(0.7, d["attenuation"], 6)

    def test_from_dict(self):
        yeast_0 = Yeast(name="Test yeast", description="A made up yeast", attenuation=0.7)
        j = json.dumps(dict(yeast_0))
        d = json.loads(j)
        yeast = Yeast.from_dict(d)
        self.assertEqual(Stage.FERMENT, Yeast.stage)
        self.assertEqual("Test yeast", yeast.name)
        self.assertEqual("A made up yeast", yeast.description)
        self.assertAlmostEqual(0.7, yeast.attenuation, 6)


if __name__ == "__main__":
    unittest.main()
