# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy.extract import Extract
from pymurgy.hop import Hop
from pymurgy.yeast import Yeast
from pymurgy.recipe import Recipe
from pymurgy.brewhouse import Brewhouse
from pymurgy.co2 import CO2
from pymurgy.common import Stage, to_plato


class TestRecipe(unittest.TestCase):
    def setUp(self):
        brewhouse = Brewhouse(
            boil_off_rate=0.14, efficiency=0.8, temp_approach=10, temp_target=19, cool_time_boil_to_target=45
        )
        # Raison d'saison from Brewing Classic Styles
        extracts = [
            Extract(stage=Stage.MASH, name="Pilsner malt", kg=4.76, max_hwe=309, deg_ebc=2.5, mashable=True),
            Extract(stage=Stage.MASH, name="Wheat malt", kg=0.34, max_hwe=311, deg_ebc=4, mashable=True),
            Extract(stage=Stage.MASH, name="Munich malt", kg=0.34, max_hwe=300, deg_ebc=15, mashable=True),
            Extract(
                stage=Stage.BOIL, name="Cane sugar", kg=0.45, max_hwe=384, deg_ebc=0, fermentability=1.0, mashable=False
            ),
        ]
        hops = [Hop(name="Hallertau", g=48, time=60, aa=0.04), Hop(name="Hallertau", g=48, time=0, aa=0.04)]
        yeast = Yeast(name="White Labs WLP565 Saison Ale", attenuation=0.75)
        co2 = CO2(volumes=3.5)
        self.recipe = Recipe(
            name="Raison d'saison",
            brewhouse=brewhouse,
            extracts=extracts,
            hops=hops,
            yeast=yeast,
            co2=co2,
            mash_time=90,
            mash_temp=64,
            boil_time=90,
            post_boil_volume=22.7,
            pitch_temp=20,
        )

    def test_pre_boil_volume(self):
        # Post-boil vol: 22.7, boil off rate: 14%/h, boil hours: 1.5
        # 22.7 / ((1 - 0.14))^1.5 = 28.4628366478
        expected = 28.4628366478
        actual = self.recipe.pre_boil_volume()
        self.assertAlmostEqual(expected, actual, 6)

    def test_og(self):
        # Brewhouse efficiency: 0.8, post-boil vol: 22.7
        # kg's, max hwe's: (4.76, 309), (0.34, 311), (0.34, 300), (0.45, 384)
        # Extract contribution formula: 1 + 0.001 * efficiency * max_hwe * self.kg / volume
        # Note that efficiency is 100% for the cane sugar addition.
        # 1 + 0.001 * 0.8 * 309 * 4.76 / 22.7 = 1.0518357
        # 1 + 0.001 * 0.8 * 311 * 0.34 / 22.7 = 1.0037265
        # 1 + 0.001 * 0.8 * 300 * 0.34 / 22.7 = 1.0035947
        # 1 + 0.001 * 1.0 * 384 * 0.45 / 22.7 = 1.0076123
        # Sum = 1.0667693
        expected = 1.0667693
        actual = self.recipe.og()
        self.assertAlmostEqual(expected, actual, 6)

    def test_post_boil_gravity(self):
        # Should be the same as og for this beer.
        expected = 1.0667693
        actual = self.recipe.post_boil_gravity()
        self.assertAlmostEqual(expected, actual, 6)

    def test_bg(self):
        # Formula: (post_boid_gravity - 1) * post_boil_volume / pre_boil_volume() + 1
        # Values from tests above ^
        # (1.0667693 - 1) * 22.7 / 28.4628366478 + 1 = 1.0532506
        expected = 1.0532506
        actual = self.recipe.bg()
        self.assertAlmostEqual(expected, actual, 6)

    def test_fg(self):
        # Formula: og - attenuation * (og - 1)
        expected = self.recipe.og() - self.recipe.attenuation() * (self.recipe.og() - 1)
        actual = self.recipe.fg()
        self.assertAlmostEqual(expected, actual, 6)

    def test_attenuation(self):
        y_att = self.recipe.yeast.attenuation
        kgs = [x.kg for x in self.recipe.extracts]
        sum_kg = sum(kgs)
        w0, w1, w2, w3 = 4.76 / sum_kg, 0.34 / sum_kg, 0.34 / sum_kg, 0.45 / sum_kg
        f0, f1, f2, f3 = w0 * y_att, w1 * y_att, w2 * y_att, w3 * 1.0
        expected = f0 + f1 + f2 + f3
        actual = self.recipe.attenuation()
        self.assertAlmostEqual(expected, actual, 6)

    def test_abv(self):
        # Annoyingly complicated formula:
        original_extract = to_plato(self.recipe.og())
        apparent_extract = to_plato(self.recipe.fg())
        q = 0.22 + 0.001 * original_extract
        real_extract = (q * original_extract + apparent_extract) / (1 + q)
        abw = (original_extract - real_extract) / (2.0665 - 0.010665 * original_extract)
        # Finally...
        expected = abw * self.recipe.fg() / 0.794
        actual = self.recipe.abv()
        self.assertAlmostEqual(expected, actual, 5)  # Did not use very precise fg and og

    def test_deg_ebc(self):
        # emcu = kg * deg_ebc / volume
        # ebc = 7.913 * sum(emcu)^0.6859
        sum_emcu = (4.76 * 2.5 + 0.34 * 4 + 0.34 * 15 + 0.45 * 0) / 22.7
        expected = 7.913 * sum_emcu**0.6859
        actual = self.recipe.deg_ebc()
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu(self):
        # Lot's of math, but we've verified all these parts in other places:
        ibu_hop_60_min = self.recipe.hops[0].ibu(
            self.recipe.bg(), self.recipe.post_boil_gravity(), 22.7, 10, 20, self.recipe.brewhouse.cooling_coefficient()
        )
        ibu_hop_0_min = self.recipe.hops[1].ibu(
            self.recipe.bg(), self.recipe.post_boil_gravity(), 22.7, 10, 20, self.recipe.brewhouse.cooling_coefficient()
        )
        expected = ibu_hop_60_min + ibu_hop_0_min
        actual = self.recipe.ibu()
        self.assertAlmostEqual(expected, actual, 6)

    def test_serialize(self):
        d_0 = dict(self.recipe)
        j = json.dumps(d_0)
        d = json.loads(j)
        # Brewhouse
        self.assertEqual(0.14, d["brewhouse"]["boil_off_rate"])
        self.assertEqual(0.8, d["brewhouse"]["efficiency"])
        self.assertEqual(10, d["brewhouse"]["temp_approach"])
        self.assertEqual(19, d["brewhouse"]["temp_target"])
        self.assertEqual(45, d["brewhouse"]["cool_time_boil_to_target"])
        # Extracts
        self.assertEqual("MASH", d["extracts"][0]["stage"])
        self.assertEqual("Pilsner malt", d["extracts"][0]["name"])
        self.assertEqual("", d["extracts"][0]["description"])
        self.assertEqual(4.76, d["extracts"][0]["kg"])
        self.assertEqual(309, d["extracts"][0]["max_hwe"])
        self.assertEqual(2.5, d["extracts"][0]["deg_ebc"])
        self.assertEqual(None, d["extracts"][0]["fermentability"])
        self.assertEqual(True, d["extracts"][0]["mashable"])
        self.assertEqual("MASH", d["extracts"][1]["stage"])
        self.assertEqual("Wheat malt", d["extracts"][1]["name"])
        self.assertEqual("", d["extracts"][1]["description"])
        self.assertEqual(0.34, d["extracts"][1]["kg"])
        self.assertEqual(311, d["extracts"][1]["max_hwe"])
        self.assertEqual(4, d["extracts"][1]["deg_ebc"])
        self.assertEqual(None, d["extracts"][1]["fermentability"])
        self.assertEqual(True, d["extracts"][1]["mashable"])
        self.assertEqual("MASH", d["extracts"][2]["stage"])
        self.assertEqual("Munich malt", d["extracts"][2]["name"])
        self.assertEqual("", d["extracts"][2]["description"])
        self.assertEqual(0.34, d["extracts"][2]["kg"])
        self.assertEqual(300, d["extracts"][2]["max_hwe"])
        self.assertEqual(15, d["extracts"][2]["deg_ebc"])
        self.assertEqual(None, d["extracts"][2]["fermentability"])
        self.assertEqual(True, d["extracts"][2]["mashable"])
        self.assertEqual("BOIL", d["extracts"][3]["stage"])
        self.assertEqual("Cane sugar", d["extracts"][3]["name"])
        self.assertEqual("", d["extracts"][3]["description"])
        self.assertEqual(0.45, d["extracts"][3]["kg"])
        self.assertEqual(384, d["extracts"][3]["max_hwe"])
        self.assertEqual(0, d["extracts"][3]["deg_ebc"])
        self.assertEqual(1.0, d["extracts"][3]["fermentability"])
        self.assertEqual(False, d["extracts"][3]["mashable"])
        self.assertEqual(4, len(d["extracts"]))
        # Hops
        self.assertEqual("BOIL", d["hops"][0]["stage"])
        self.assertEqual("Hallertau", d["hops"][0]["name"])
        self.assertEqual(48, d["hops"][0]["g"])
        self.assertEqual(60, d["hops"][0]["time"])
        self.assertEqual(0.04, d["hops"][0]["aa"])
        self.assertEqual("BOIL", d["hops"][1]["stage"])
        self.assertEqual("Hallertau", d["hops"][1]["name"])
        self.assertEqual(48, d["hops"][1]["g"])
        self.assertEqual(0, d["hops"][1]["time"])
        self.assertEqual(0.04, d["hops"][1]["aa"])
        self.assertEqual(2, len(d["hops"]))
        # Yeast
        self.assertEqual("FERMENT", d["yeast"]["stage"])
        self.assertEqual("White Labs WLP565 Saison Ale", d["yeast"]["name"])
        self.assertEqual("", d["yeast"]["description"])
        self.assertEqual(0.75, d["yeast"]["attenuation"])
        # CO2
        self.assertEqual("CONDITION", d["co2"]["stage"])
        self.assertEqual(3.5, d["co2"]["volumes"])
        # Data
        self.assertEqual("Raison d'saison", d["name"])
        self.assertEqual(90, d["mash_time"])
        self.assertEqual(64, d["mash_temp"])
        self.assertEqual(90, d["boil_time"])
        self.assertEqual(22.7, d["post_boil_volume"])
        self.assertEqual(20, d["pitch_temp"])

    def test_from_dict(self):
        j = json.dumps(dict(self.recipe))
        d = json.loads(j)
        recipe: Recipe = Recipe.from_dict(d)
        # Brewhouse
        self.assertEqual(0.14, recipe.brewhouse.boil_off_rate)
        self.assertEqual(0.8, recipe.brewhouse.efficiency)
        self.assertEqual(10, recipe.brewhouse.temp_approach)
        self.assertEqual(19, recipe.brewhouse.temp_target)
        self.assertEqual(45, recipe.brewhouse.cool_time_boil_to_target)
        # Extracts
        self.assertEqual(Stage.MASH, recipe.extracts[0].stage)
        self.assertEqual("Pilsner malt", recipe.extracts[0].name)
        self.assertEqual("", recipe.extracts[0].description)
        self.assertEqual(4.76, recipe.extracts[0].kg)
        self.assertEqual(309, recipe.extracts[0].max_hwe)
        self.assertEqual(2.5, recipe.extracts[0].deg_ebc)
        self.assertEqual(True, recipe.extracts[0].mashable)
        self.assertEqual(Stage.MASH, recipe.extracts[1].stage)
        self.assertEqual("Wheat malt", recipe.extracts[1].name)
        self.assertEqual("", recipe.extracts[1].description)
        self.assertEqual(0.34, recipe.extracts[1].kg)
        self.assertEqual(311, recipe.extracts[1].max_hwe)
        self.assertEqual(4, recipe.extracts[1].deg_ebc)
        self.assertEqual(True, recipe.extracts[1].mashable)
        self.assertEqual(Stage.MASH, recipe.extracts[2].stage)
        self.assertEqual("Munich malt", recipe.extracts[2].name)
        self.assertEqual("", recipe.extracts[2].description)
        self.assertEqual(0.34, recipe.extracts[2].kg)
        self.assertEqual(300, recipe.extracts[2].max_hwe)
        self.assertEqual(15, recipe.extracts[2].deg_ebc)
        self.assertEqual(True, recipe.extracts[2].mashable)
        self.assertEqual(Stage.BOIL, recipe.extracts[3].stage)
        self.assertEqual("Cane sugar", recipe.extracts[3].name)
        self.assertEqual("", recipe.extracts[3].description)
        self.assertEqual(0.45, recipe.extracts[3].kg)
        self.assertEqual(384, recipe.extracts[3].max_hwe)
        self.assertEqual(0, recipe.extracts[3].deg_ebc)
        self.assertEqual(False, recipe.extracts[3].mashable)
        self.assertEqual(4, len(recipe.extracts))
        ## Hops
        self.assertEqual(Stage.BOIL, recipe.hops[0].stage)
        self.assertEqual("Hallertau", recipe.hops[0].name)
        self.assertEqual(48, recipe.hops[0].g)
        self.assertEqual(60, recipe.hops[0].time)
        self.assertEqual(0.04, recipe.hops[0].aa)
        self.assertEqual(Stage.BOIL, recipe.hops[1].stage)
        self.assertEqual("Hallertau", recipe.hops[1].name)
        self.assertEqual(48, recipe.hops[1].g)
        self.assertEqual(0, recipe.hops[1].time)
        self.assertEqual(0.04, recipe.hops[1].aa)
        self.assertEqual(2, len(recipe.hops))
        ## Yeast
        self.assertEqual(Stage.FERMENT, recipe.yeast.stage)
        self.assertEqual("White Labs WLP565 Saison Ale", recipe.yeast.name)
        self.assertEqual("", recipe.yeast.description)
        self.assertEqual(0.75, recipe.yeast.attenuation)
        # CO2
        self.assertEqual(Stage.CONDITION, recipe.co2.stage)
        self.assertEqual(3.5, recipe.co2.volumes)
        ## Data
        self.assertEqual("Raison d'saison", recipe.name)
        self.assertEqual(90, recipe.mash_time)
        self.assertEqual(64, recipe.mash_temp)
        self.assertEqual(90, recipe.boil_time)
        self.assertEqual(22.7, recipe.post_boil_volume)
        self.assertEqual(20, recipe.pitch_temp)


if __name__ == "__main__":
    unittest.main()
