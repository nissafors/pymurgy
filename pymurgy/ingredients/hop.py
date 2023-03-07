import math
from dataclasses import dataclass
from .ingredient import Ingredient
from ..calc import cool_time, celsius_to_kelvin
from ..common import Stage


@dataclass
class Hop(Ingredient):
    """Represents a hop addition.

    Properties:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        name (str): The name of the hop.
        g (float): The amount of the hop in grams.
        time (int): Boil time in minutes.
        aa (float): Alpha acid content expressed as a decimal number (0.14 = 14%).
    """

    name: str = ""
    g: float = 0.0
    time: int = 0
    aa: float = 0.0

    def compute_boil_utilization(self, pre_boil_gravity: float, post_boil_gravity: float) -> float:
        """Calculate hop utilization from boil using Tinseth's formula.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts.
            post_boil_gravity (float): Specific gravity at flameout.

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

    def compute_post_boil_utilization(
        self,
        pre_boil_gravity: float,
        post_boil_gravity: float,
        temp_approach: int,
        temp_target: int,
        cooling_coefficient: float,
    ) -> float:
        """Calculate post-boil hop utilization using a simplified mIBU algorithm.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts.
            post_boil_gravity (float): Specific gravity at flameout.
            temp_approach (int): Approaching temperature, e.g. ground water temperature for immersion chillers.
            temp_target (int): Temperature reached in cool_time minutes. Must be higher than temp_surround.
            cooling_coefficient (float): See calc.cooling_coefficient().

        Returns:
            float: Alpha acid utilization factor.
        """
        # Adapted from: https://alchemyoverlord.wordpress.com/2015/05/12/a-modified-ibu-measurement-especially-for-late-hopping/
        integration_time = 0.001
        decimal_alpha_acid_utilization = 0.0
        t = self.time
        sg = float(pre_boil_gravity + post_boil_gravity) / 2.0
        ct = cool_time(temp_approach, temp_target, cooling_coefficient)
        while t < self.time + ct:
            dU = -1.65 * 0.000125 ** (sg - 1.0) * -0.04 * math.e ** (-0.04 * t) / 4.15
            temp_kelvin = celsius_to_kelvin(
                (100 - temp_approach) * math.e ** (-1.0 * cooling_coefficient * (t - self.time)) + temp_approach
            )
            degree_of_utilization = 2.39 * 10.0**11.0 * math.e ** (-9773.0 / temp_kelvin)
            if t < 5.0:
                degree_of_utilization = 1.0  # account for nonIAA components
            combined_value = dU * degree_of_utilization
            decimal_alpha_acid_utilization += combined_value * integration_time
            t += integration_time
        return decimal_alpha_acid_utilization

    def ibu(
        self,
        pre_boil_gravity: float,
        post_boil_gravity: float,
        volume: int,
        temp_surround: int,
        temp_target: int,
        cooling_coefficient: float,
    ) -> float:
        """Compute bitternes contribution.

        Args:
            pre_boil_gravity (float): Specific gravity when the boil starts.
            post_boil_gravity (float): Specific gravity at flameout.
            volume (int): Post-boil volume in litres.
            temp_approach (int): Approaching temperature, e.g. ground water temperature for immersion chillers.
            temp_target (int): Temperature reached in cool_time minutes. Must be higher than temp_surround.
            cooling_coefficient (float): See common.compute_cooling_coefficient().

        Returns:
            float: Estimated IBU contribution.
        """
        # IBU = D * U              (D is density of AA in wort in mg/l, U is utilization)
        #       D = AA * 10m  / V  (AA is alpha acid content, m in grams and V is post-boil volume in litres)
        #       U = Ub + Up        (Ub is utilization during boil and Up is post-boil utilization)
        # For Ub and Ub, see self.compute_boil_utilization() and self.compute_post_boil_utilization().
        if self.stage == Stage.BOIL:
            u_b = self.compute_boil_utilization(pre_boil_gravity, post_boil_gravity)
            u_p = self.compute_post_boil_utilization(
                pre_boil_gravity, post_boil_gravity, temp_surround, temp_target, cooling_coefficient
            )
            ibu = (u_b + u_p) * self.aa * 1000.0 * self.g / volume
        else:
            # Mash hopping and dry hopping contributes essentially no bitterness, at least not in a predictable way.
            ibu = 0.0
        return ibu
