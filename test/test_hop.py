# fmt: off
import sys, pathlib
# Allow us to import from parent folder
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
# fmt: on

import unittest, json
from pymurgy import Hop, Stage
from pymurgy.calc import cooling_coefficient

# Set to True to to plot example graphs of hop utilization and temperature over time using pyplot.
test_graph = False
if test_graph:
    import matplotlib.pyplot as plt

test_performance = False
if test_performance:
    import time


class TestHop(unittest.TestCase):
    def setUp(self):
        self.k = cooling_coefficient(7.0, 20.0, 40.0)

    @unittest.skipUnless(test_graph, "Set test_graph to True to run. Requires matplotlib.")
    def test_graph(self):
        """Show two example graphs (utilization and ibu) for a few hops."""
        Hop.store_graph = True
        hop60min = Hop(g=20, time=60, aa=0.1)
        hop30min = Hop(g=40, time=30, aa=0.1)
        hop5min = Hop(g=50, time=5, aa=0.05)
        hop60min.utilization_mibu(1.055, 1.065, 7, 20, self.k, 60, 20, 5)
        hop30min.utilization_mibu(1.055, 1.065, 7, 20, self.k, 60, 20, 5)
        hop5min.utilization_mibu(1.055, 1.065, 7, 20, self.k, 60, 20, 5)
        # Graph utilization
        fig, ax1 = plt.subplots()
        ax1.set_xlabel("time (min)")
        ax1.set_ylabel("temp", color="tab:red")
        ax1.plot(hop5min.graph["time"], hop5min.graph["temperature"], color="tab:red")
        ax1.tick_params(axis="y", labelcolor="tab:red")
        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis.
        ax2.set_ylabel("utilization", color="tab:blue")
        ax2.plot(hop60min.graph["time"], hop60min.graph["utilization"], color="tab:blue")
        ax2.plot(hop30min.graph["time"], hop30min.graph["utilization"], color="tab:green")
        ax2.plot(hop5min.graph["time"], hop5min.graph["utilization"], color="tab:purple")
        ax2.tick_params(axis="y", labelcolor="tab:blue")
        fig.tight_layout()  # Otherwise the right y-label is slightly clipped.
        plt.show()
        # Graph IBU contribution
        del ax1
        del ax2
        del fig
        fig, ax1 = plt.subplots()
        ax1.set_xlabel("time (min)")
        ax1.set_ylabel("temp", color="tab:red")
        ax1.plot(hop5min.graph["time"], hop5min.graph["temperature"], color="tab:red")
        ax1.tick_params(axis="y", labelcolor="tab:red")
        ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis.
        ax2.set_ylabel("IBU", color="tab:blue")
        ax2.plot(hop60min.graph["time"], hop60min.graph["ibu"], color="tab:blue")
        ax2.plot(hop30min.graph["time"], hop30min.graph["ibu"], color="tab:green")
        ax2.plot(hop5min.graph["time"], hop5min.graph["ibu"], color="tab:purple")
        ax2.tick_params(axis="y", labelcolor="tab:blue")
        fig.tight_layout()  # Otherwise the right y-label is slightly clipped.
        plt.show()

    @unittest.skipUnless(test_performance, "Set test_performance to True to run.")
    def test_performance(self):
        """Compute and print basic performance info."""
        hop_list = [Hop(g=10, time=30, aa=0.1) for t in range(0, 60, 3)]
        for hop in hop_list:
            hop.store_graph = True
        print(
            f"\nCompute ibu for {len(hop_list)} hop additions with addition times distributed over 60 min boil time..."
        )
        t_0 = time.process_time()
        for i, hop in enumerate(hop_list):
            hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20, 10)
        t_total = time.process_time() - t_0
        total_elements = sum(
            [
                len(x.graph["time"]) + len(x.graph["temperature"]) + len(x.graph["utilization"]) + len(x.graph["ibu"])
                for x in hop_list
            ]
        )
        print(f"  Total process time (s): {t_total}")
        print(f"  Graph total elements: {total_elements}")

    def test_utilization_mibu(self):
        hop = Hop(time=6)
        expected = 0.1053861  # Pre-calculated
        actual = hop.utilization_mibu(1.055, 1.065, 7, 20, self.k, 60, 20, 15)
        self.assertAlmostEqual(expected, actual, 6)
        hop = Hop(time=45)
        expected = 0.1980619  # Pre-calculated
        actual = hop.utilization_mibu(1.055, 1.065, 7, 20, self.k, 60, 20)
        self.assertAlmostEqual(expected, actual, 6)

    def test_utilization_tinseth(self):
        hop = Hop(time=6)
        expected = 0.0494753  # Pre-calculated
        actual = hop.utilization_tinseth(1.055, 1.065)
        self.assertAlmostEqual(expected, actual, 6)
        hop = Hop(time=45)
        expected = 0.1935448  # Pre-calculated
        actual = hop.utilization_tinseth(1.055, 1.065)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu_boil(self):
        # No whirlpool
        hop = Hop(stage=Stage.BOIL, g=60, time=10, aa=0.10)
        expected = 27.5116176  # Pre-calculated
        actual = hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20)
        self.assertAlmostEqual(expected, actual, 6)
        # 15 min whirlpool
        expected = 36.9054303  # Pre-calculated
        k = cooling_coefficient(20.0, 25.0, 20.0)
        actual = hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20, 15)
        self.assertAlmostEqual(expected, actual, 6)

    def test_ibu_ferment(self):
        hop = Hop(stage=Stage.FERMENT, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20, 15)
        self.assertEqual(expected, actual)

    def test_ibu_mash(self):
        hop = Hop(stage=Stage.MASH, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20, 15)
        self.assertEqual(expected, actual)

    def test_ibu_tinseth_boil(self):
        hop = Hop(stage=Stage.BOIL, g=50, time=60, aa=0.10)
        mibu = hop.ibu(1.055, 1.065, 7, 20, self.k, 60, 20)
        tinseth = hop.ibu_tinseth(1.055, 1.065, 20)
        # On a 60 min addition it shouldn't diff too much, at least not more than 5 IBU.
        self.assertTrue(abs(mibu - tinseth) < 5)

    def test_ibu_tinseth_ferment(self):
        hop = Hop(stage=Stage.FERMENT, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu_tinseth(1.055, 1.065, 60)
        self.assertEqual(expected, actual)

    def test_ibu_tinseth_mash(self):
        hop = Hop(stage=Stage.MASH, g=56.7, time=6, aa=0.10)
        expected = 0.0
        actual = hop.ibu_tinseth(1.055, 1.065, 60)
        self.assertEqual(expected, actual)

    def test_serialize(self):
        hop = Hop(stage=Stage.FERMENT, name="Test hop", g=10.5, time=15, aa=0.05)
        d_0 = dict(hop)
        self.assertNotIn("graph", d_0.keys())
        self.assertNotIn("store_graph", d_0.keys())
        self.assertNotIn("integration_time", d_0.keys())
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
