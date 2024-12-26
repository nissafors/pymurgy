import math
from dataclasses import dataclass
from typing import ClassVar
from .ingredient import Ingredient
from ..calc import cool_time, celsius_to_kelvin, kelvin_to_celsius
from ..common import Stage


@dataclass
class Hop(Ingredient):
    """Represents a hop addition.

    Args:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        name (str): The name of the hop.
        g (float): The amount of the hop in grams.
        time (int): Boil time in minutes.
        aa (float): Alpha acid content expressed as a decimal number (0.14 = 14%).

    Class variables:
        store_graph (bool): Set to True to store data for graphing. See graph below. Default: False.
        integration_time (float): Utilization integration time resolution (minutes/snapshot). Default: 1/60. A lower
                number yields more precise calculations and higher resolution graph data, but is also slower and -
                if store_graph is True - consumes more memory. Try increasing the number if you experience performance
                issues.

    Properties:
        graph (dict): Data for graphing accessed via graph["temperature"], graph["utilization], graph["ibu"] and
                graph["time"]. Given that store_graph is True, this data is available after a call to the ibu()
                or to the utilization_mibu() methods. Note that graph data is not recorded for the ibu_tinseth() or the
                utilization_tinseth() methods.
    """

    name: str = ""
    g: float = 0.0
    time: int = 0
    aa: float = 0.0
    integration_time: ClassVar[float] = 1 / 60
    store_graph: ClassVar[bool] = False

    def __post_init__(self):
        """Post intialization duties."""
        self.reset_graph()

    def utilization_mibu(
        self,
        pre_boil_gravity: float,
        post_boil_gravity: float,
        temp_approach: int,
        temp_target: int,
        cooling_coefficient: float,
        boil_time: int,
        post_boil_volume: float,
        whirlpool_time: int = 0,
        surface_area: int = 900,
        opening_area: int = None,
    ) -> float:
        """Calculate hop utilization with the maximum IBU (mIBU) method.

        Whirlpool is defined here as the time the wort cools naturally from boiling after flameout. Set whirlpool_time
        to 0 when whirlpooling while simultaneously force cooling.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts as a decimal number (e.g. 1.040).
            post_boil_gravity (float): Specific gravity at flameout as a decimal number (e.g. 1.050).
            temp_approach (int): Approach temperature in degrees Celsius (e.g. ground water temperature for immersion
                    chillers).
            temp_target (int): Pitch temperature in degrees Celsius.
            cooling_coefficient (float): Cooling coefficient for used cooling method. See calc.cooling_coefficient().
            boil_time (int): Total boil time in minutes.
            post_boil_volume (int): Post-boil volume in litres.
            whirlpool_time (int): Whirlpool time in minutes.
            surface_area (int): Wort surface are in liters. Used for estimating natural cooling during whirlpool,
                    ignored when whirlpool_time is 0. Default: 900.
            opening_area (int): Kettel opening are in liters. surface_area is used when set to None. Used for
                    estimating natural cooling during whirlpool, ignored when whirlpool_time is 0.  Default: None.

        Returns:
            float: Alpha acid utilization factor.
        """
        # Adapted from: https://alchemyoverlord.wordpress.com/2015/05/12/a-modified-ibu-measurement-especially-for-late-hopping/
        if self.store_graph:
            self.reset_graph()
            self.graph["time"].append(0)
            self.graph["temperature"].append(100.0)
            self.graph["utilization"].append(None)
        k_extract = (post_boil_gravity - 1) * post_boil_volume
        pre_boil_volume = k_extract / (pre_boil_gravity - 1)
        boil_off_rate = 1 - (post_boil_volume / pre_boil_volume) ** (1 / boil_time)
        add_time = boil_time - self.time
        gravity = post_boil_gravity
        if opening_area is None:
            opening_area = surface_area
        util_time = self.time + whirlpool_time
        t = 0.0
        temp_k = celsius_to_kelvin(100)
        u_total = 0.0
        whirlpool_done = False
        while True:
            # Integrate utilization
            if t >= util_time:
                if not whirlpool_done:
                    whirlpool_done = True
                    temp_post_whirlpool = kelvin_to_celsius(temp_k)
                    util_time += cool_time(temp_approach, temp_target, cooling_coefficient, temp_post_whirlpool)
                else:
                    break
            if t < self.time:
                # Gravity changes during boil but not temperature.
                gravity = 1 + k_extract / (pre_boil_volume * (1 - boil_off_rate) ** (add_time + t))
            elif t < self.time + whirlpool_time:
                # John-Paul Hosom (alchemyoverlord) gives the following formula for natural cooling:
                #   T = 53.7 × exp(-b × t) + 319.55,
                # where T is temperature at t mins after flameout and b:
                #   b = 0.0002925 × (surfaceArea × openingArea)^0.5 / volume + 0.00538
                # Hosom chose 100.1C as the initial temperature and we can see the formula above is then equal to:
                #   T = (100.1 - 46.4) × exp(-b × t) + 46.4 + 273.15
                # We want to start at 100 because that's where things boil, right? We don't care about minor details
                # such as wort boiling at slightly higher temperature than water and at what elevation we're at. No
                # IBU prediction method is accurate enough to warrant such attention to detail.
                b = 0.0002925 * math.sqrt(surface_area * opening_area) / post_boil_volume + 0.00538
                temp_k = 53.6 * math.exp(-1.0 * b * (t - self.time)) + 319.55
            else:
                # Forced cooling rates will depend heavily on the equipment used, so in this case we must rely the user
                # to provide a cooling constant.
                temp_k = celsius_to_kelvin(
                    (temp_post_whirlpool - temp_approach)
                    * math.exp(-1.0 * cooling_coefficient * (t - whirlpool_time - self.time))
                    + temp_approach
                )
            dU = -1.65 * 0.000125 ** (gravity - 1.0) * -0.04 * math.exp(-0.04 * t) / 4.15
            degree_of_utilization = min(1.0, 2.39 * 10.0**11.0 * math.exp(-9773.0 / temp_k))
            if t < 5.0:
                degree_of_utilization = 1.0  # account for nonIAA components
            combined_value = dU * degree_of_utilization
            u_total += combined_value * self.integration_time
            if self.store_graph:
                self.graph["time"].append(add_time + t)
                self.graph["temperature"].append(kelvin_to_celsius(temp_k))
                self.graph["utilization"].append(combined_value)
            t = t + self.integration_time
        if self.store_graph:
            self.graph["ibu"] = [u if u is None else self._ibu(u, post_boil_volume) for u in self.graph["utilization"]]
        return u_total

    def utilization_tinseth(self, pre_boil_gravity: float, post_boil_gravity: float) -> float:
        """Calculate hop utilization with Tinseth's method.

        This is a much simpler approach than the recommended mIBU method (which in turn builds upon Tinseth's
        formulae) that does not account for hop utilization after flameout.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts as a decimal number (e.g. 1.040).
            post_boil_gravity (float): Specific gravity at flameout as a decimal number (e.g. 1.050).

        Returns:
            float: Alpha acid utilization factor.
        """
        # Quotes from Tinseth (https://www.realbeer.com/hops/research.html).
        # "The Bigness factor accounts for reduced utilization due to higher wort gravities.
        # Use an average gravity value for the entire boil to account for changes in the wort volume.""
        bigness_factor = 1.65 * 0.000125 ** ((pre_boil_gravity + post_boil_gravity) / 2.0 - 1.0)
        # "The Boil Time factor accounts for the change in utilization due to boil time:"
        boil_time_factor = (1.0 - math.e ** (-0.04 * self.time)) / 4.15
        return bigness_factor * boil_time_factor

    def ibu(
        self,
        pre_boil_gravity: float,
        post_boil_gravity: float,
        temp_approach: int,
        temp_target: int,
        cooling_coefficient: float,
        boil_time: int,
        post_boil_volume: float,
        whirlpool_time: int = 0,
        surface_area: int = 900,
        opening_area: int = None,
    ) -> float:
        """Compute bitternes contribution with the maximum IBU (mIBU) method.

        Whirlpool is defined here as the time the wort cools naturally from boiling after flameout. Set whirlpool_time
        to 0 when whirlpooling while simultaneously force cooling.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts as a decimal number (e.g. 1.040).
            post_boil_gravity (float): Specific gravity at flameout as a decimal number (e.g. 1.050).
            temp_approach (int): Approach temperature in degrees Celsius (e.g. ground water temperature for immersion
                    chillers).
            temp_target (int): Pitch temperature in degrees Celsius.
            cooling_coefficient (float): Cooling coefficient for used cooling method. See calc.cooling_coefficient().
            boil_time (int): Total boil time in minutes.
            post_boil_volume (int): Post-boil volume in litres.
            whirlpool_time (int): Whirlpool time in minutes.
            surface_area (int): Wort surface are in liters. Used for estimating natural cooling during whirlpool,
                    ignored when whirlpool_time is 0. Default: 900.
            opening_area (int): Kettel opening are in liters. surface_area is used when set to None. Used for
                    estimating natural cooling during whirlpool, ignored when whirlpool_time is 0.  Default: None.

        Returns:
            float: Estimated bitterness contribution in International Bitternes Units (IBU).
        """
        # IBU = D * U              (D is density of AA in wort in mg/l, U is utilization)
        #       D = AA * 10m  / V  (AA is alpha acid content, m in grams and V is post-boil volume in litres)
        if self.stage == Stage.BOIL:
            u = self.utilization_mibu(
                pre_boil_gravity,
                post_boil_gravity,
                temp_approach,
                temp_target,
                cooling_coefficient,
                boil_time,
                post_boil_volume,
                whirlpool_time,
                surface_area,
                opening_area,
            )
            ibu = self._ibu(u, post_boil_volume)
        else:
            # Mash hopping and dry hopping contributes essentially no bitterness, at least not in a predictable way.
            ibu = 0.0
        return ibu

    def ibu_tinseth(self, pre_boil_gravity: float, post_boil_gravity: float, post_boil_volume: float) -> float:
        """Compute bitternes contribution with Tinseth's method.

        This is a much simpler approach than the recommended mIBU method (which in turn is builds upon Tinseth's
        formulae) that does not account for hop utilization after flameout.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts as a decimal number (e.g. 1.040).
            post_boil_gravity (float): Specific gravity at flameout as a decimal number (e.g. 1.050).
            post_boil_volume (int): Post-boil volume in litres.

        Returns:
            float: Estimated bitterness contribution in International Bitternes Units (IBU).
        """
        if self.stage == Stage.BOIL:
            u = self.utilization_tinseth(pre_boil_gravity, post_boil_gravity)
            ibu = self._ibu(u, post_boil_volume)
        else:
            ibu = 0.0
        return ibu

    def reset_graph(self):
        """Clear graph data."""
        self.graph = {"time": [], "temperature": [], "utilization": []}

    def _ibu(self, utilization, post_boil_volume):
        """Compute IBUs."""
        return utilization * self.aa * 1000.0 * self.g / post_boil_volume

    def __iter__(self):
        for k, v in super().__iter__():
            if k == "graph":
                # Skip non-dataclass members.
                continue
            else:
                yield k, v
