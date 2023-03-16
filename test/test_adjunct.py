# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Adjunct, Stage


class TestAdjunct(unittest.TestCase):
    def setUp(self):
        self.adjunct = Adjunct(
            stage=Stage.BOIL,
            name="Test adjunct",
            description="A made up adjunct",
            instructions="Detailed instructions",
            kg=0.5,
        )

    def test_serialize(self):
        d_0 = dict(self.adjunct)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("BOIL", d["stage"])
        self.assertEqual("Test adjunct", d["name"])
        self.assertEqual("A made up adjunct", d["description"])
        self.assertEqual("Detailed instructions", d["instructions"])
        self.assertEqual(0.5, d["kg"])

    def test_from_dict(self):
        j = json.dumps(dict(self.adjunct))
        d = json.loads(j)
        adjunct: Adjunct = Adjunct.from_dict(d)
        self.assertEqual(Stage.BOIL, adjunct.stage)
        self.assertEqual("Test adjunct", adjunct.name)
        self.assertEqual("A made up adjunct", adjunct.description)
        self.assertEqual("Detailed instructions", adjunct.instructions)
        self.assertEqual(0.5, adjunct.kg)


if __name__ == "__main__":
    unittest.main()
