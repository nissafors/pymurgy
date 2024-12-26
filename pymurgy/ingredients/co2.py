from dataclasses import dataclass, field
from ..common import Stage
from ..ingredients.ingredient import Ingredient
from ..ingredients.extract import Fermentable
from ..calc import celsius_to_fahrenheit, to_bar, to_litres


@dataclass
class CO2(Ingredient):
    """Represents beer carbonation.

    Args:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        volumes (float): Number of volume units of CO2 per volume unit of beer.
    """

    stage: Stage = field(default_factory=lambda: Stage.CONDITION)
    volumes: float = 0.0

    def force_carbonation_pressure(self, temp: float) -> float:
        """Calculate pressure level for force carbonation.

        Args:
            temp (float): Beer temperature in degrees Celsius.

        Returns:
            float: Pressure in bar.
        """
        # This seems to be the most common approximation used by a lot of calculators online.
        # Original source: http://hbd.org/hbd/archive/2788.html#2788-8
        v = self.volumes
        t = celsius_to_fahrenheit(temp)
        psi = -16.6999 - 0.0101059 * t + 0.00116512 * t**2 + 0.173354 * t * v + 4.24267 * v - 0.0684226 * v**2
        return to_bar(psi)

    def priming(
        self, volume: float, temp: float, hwe: float = Fermentable.SUCROSE.hwe, fermemtability: float = 1.0
    ) -> float:
        """Calculate amount of priming sugar for carbonation.

        Args:
            volume (float): The amount of beer in each package unit in liter.
            temp (float): Beer temperature when priming in degrees Celsius. This is used to determine the amount of CO2
                    already present in the beer when adding the sugar. The user must take into account if the beer was
                    cooled or warmed recently and try to judge what is a representative temperature.
            hwe (int): Priming sugar HWE in liter degrees per kilogram. Default: 384 (sucrose).

        Returns:
            float: Amount of priming sugar per package unit in grams.
        """
        t = celsius_to_fahrenheit(temp)
        priming_type_factor = Fermentable.SUCROSE.hwe / (fermemtability * hwe)
        # Formulae from: https://www.homebrewersassociation.org/attachments/0000/2497/Math_in_Mash_SummerZym95.pdf
        # Seems to be widely used. This first part is fit "to some empirical data" and represents the amount of CO2
        # already dissolved in the beer (in volumes):
        cd_init = 3.0378 - 0.050062 * t + 0.00026555 * t**2
        # The next part can be derived from the fermentation reaction: C6H12O6 -> 2 C2H3OH + 2 CO2
        # So 2 parts CO2 from each part C6H12O6. Weights are 180.156g C6H12O6/mol and 44.009g CO2/mol. This gives:
        #   CD_gen = PS * (2 * 44.009 / 180.156)(1 / Q)(1 / V)
        # ...where PS = grams of priming sugar, Q = grams of CO2 per volume unit and V is beer volume.
        # In the article gallons is used as volume unit with a value of Q = 7.4287. I don't understand how he arrives
        # at this value, but for now let's just convert it to liters. Solve for PS and we get:
        #   PS = 2 * 44.009 * V / (180.156 * Q * CD_gen)
        cd_gen = self.volumes - cd_init
        q = 7.4287 / to_litres(1)
        ps = volume * 180.156 * q * cd_gen / (2 * 44.009)
        # Account for different priming sugars
        return ps * priming_type_factor
