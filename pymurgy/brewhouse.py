# fmt: off
# Make sure we can always import from ./ no matter where we're called from
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
# fmt: on

from dataclasses import dataclass
from common import Serializable, compute_cooling_coefficient


@dataclass
class Brewhouse(Serializable):
    """Represents The brewhouse.

    Properties:
        boil_off_rate (float): The rate of evaporation per hour.
        efficiency (float): Brew house efficiency.
        temp_approach (int): Lower wort temperature limit for the chilling procedure in degrees Celsius.
        temp_target (int): A target wort temperature in degreess Celsius for which the cooling time from boil is known.
        cool_time_boil_to_target (int): The time in minutes it takes to cool the wort from boiling to temp_target.
    """

    boil_off_rate: float = 0.14
    efficiency: float = 0.75
    temp_approach: int = 15
    temp_target: int = 20
    cool_time_boil_to_target: int = 30

    def cooling_coefficient(self) -> float:
        """Get the cooling coefficient for this brewhouse."""
        return compute_cooling_coefficient(self.temp_approach, self.temp_target, self.cool_time_boil_to_target, 100)
