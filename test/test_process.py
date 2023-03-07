# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from dataclasses import dataclass, field
from pymurgy import Process, Temperature


class TestProcess(unittest.TestCase):
    def test_serialize(self):
        temp = Temperature(temp_init=10, temp_final=20, time=30)
        temps = [Temperature(temp_init=65, temp_final=65, time=60), Temperature(temp_init=75, temp_final=75, time=10)]
        test_class = TestClass(instructions="Test instructions", temp=temp, temps=temps)
        d_0 = dict(test_class)
        j = json.dumps(d_0)
        d = json.loads(j)
        self.assertEqual("Test instructions", d["instructions"])
        self.assertEqual(10, d["temp"]["temp_init"])
        self.assertEqual(20, d["temp"]["temp_final"])
        self.assertEqual(30, d["temp"]["time"])
        self.assertEqual(65, d["temps"][0]["temp_init"])
        self.assertEqual(65, d["temps"][0]["temp_final"])
        self.assertEqual(60, d["temps"][0]["time"])
        self.assertEqual(75, d["temps"][1]["temp_init"])
        self.assertEqual(75, d["temps"][1]["temp_final"])
        self.assertEqual(10, d["temps"][1]["time"])

    def test_from_dict(self):
        temp = Temperature(temp_init=10, temp_final=20, time=30)
        temps = [Temperature(temp_init=65, temp_final=65, time=60), Temperature(temp_init=75, temp_final=75, time=10)]
        test_class_0 = TestClass(instructions="Test instructions", temp=temp, temps=temps)
        j = json.dumps(dict(test_class_0))
        d = json.loads(j)
        test_class: TestClass = TestClass.from_dict(d)
        self.assertEqual("Test instructions", d["instructions"])
        self.assertEqual(10, test_class.temp.temp_init)
        self.assertEqual(20, test_class.temp.temp_final)
        self.assertEqual(30, test_class.temp.time)
        self.assertEqual(65, test_class.temps[0].temp_init)
        self.assertEqual(65, test_class.temps[0].temp_final)
        self.assertEqual(60, test_class.temps[0].time)
        self.assertEqual(75, test_class.temps[1].temp_init)
        self.assertEqual(75, test_class.temps[1].temp_final)
        self.assertEqual(10, test_class.temps[1].time)


@dataclass
class TestClass(Process):
    temp: Temperature = 0
    temps: list[Temperature] = field(default_factory=list)


if __name__ == "__main__":
    unittest.main()
