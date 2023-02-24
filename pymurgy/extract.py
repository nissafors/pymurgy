# fmt: off
# Make sure we can always import from ./ no matter where we're called from
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
# fmt: on

from dataclasses import dataclass
from common import Stage, Ingredient, ComparableEnum, AutoIncrementEnum


class Fermentable(ComparableEnum, AutoIncrementEnum):
    """Convenience enum for standard fermentables with known HWE and fermentability.

    Yeast attenuation will be used when fermentability is None.

    Properties:
        hwe (int): HWE as liter degrees per kilogram.
        fermentability (float): Fermentability as a float between 0 and 1 (or None to use expected Yeast attenuation).
    """

    LME = (300, None)
    DME = (375, None)
    SUCROSE = (384, 1.0)
    CORN_SUGAR = (351, 1.0)
    RICE_SYRUP_SOLIDS = (351, 0.8)
    MOLASSES = (300, 0.9)
    CANDI_SUGAR = (384, 1.0)
    LACTOSE = (384, 0.0)
    HONEY = (317, 0.95)
    MAPLE_SYRUP = (259, 1.0)
    MALTODEXTRIN = (351, 0.0)

    def __init__(self, hwe: int, fermentability: float):
        """Creates a new ExtractType."""
        self._max_hwe = hwe
        self._fermentability = fermentability

    @property
    def hwe(self) -> int:
        """HWE (liter degrees per kilogram) for the sugar."""
        return self._max_hwe

    @property
    def fermentability(self) -> float:
        """Fermentability as a float between 0 and 1."""
        return self._fermentability


@dataclass
class Extract(Ingredient):
    """Represents an extract giver.

    Properties:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        name (str): The name of the extract giver.
        description (str): Optional description of the extract giver (malt, LME, DME, sugar etc).
        kg (float): The amount of the extract giver in kilograms.
        max_hwe (int): Max hot water extract in liter degrees per kilogram.
        deg_ebc (float): Color contribution in degrees EBC.
        fermentability (float): How much of the sugar content that any yeast is expected to ferment as a float between
                0 and 1. If set to None, or if mashable is True, the expected attenuation for the Yeast will be used
                instead, which is typically what you want for e.g. mashed grains, DME or LME.
        mashable (bool): True if the extract giver can be mashed or steeped.
    """

    name: str = ""
    description: str = ""
    kg: float = 0.0
    max_hwe: int = 0
    deg_ebc: float = 0.0
    fermentability: float = None
    mashable: bool = False

    def hwe(self, efficiency: float) -> float:
        """Return expected HWE with given efficiency."""
        return self.max_hwe * efficiency

    def sg(
        self, volume: float, efficiency: float, include_post_boil: bool = True, steeping_efficiency: float = 0.35
    ) -> float:
        """Return expected contribution to original gravity.

        Args:
            volume: Volume in litres.
            efficiency: Brewhouse efficiency as decimal, i.e. give 75% as 0.75.
            include_post_boil: If False sugar additions to the fermentation vessel returns 0. Good for
                               post-boil-and-pre-fermentation gravity calculations.
            steeping_efficiency: Efficiency coefficient for steeping grains.

        Returns:
            Efficiency as specific gravity, e.g. 1.040.
        """
        if self.mashable and self.stage == Stage.FERMENT:
            # Adding a mashable to the fermenter would be a stupid thing. Let's call that zero efficiency.
            efficiency = 0.0
        elif self.mashable and self.stage == Stage.BOIL:
            # Adding a mashable to the boil indicates it's a steeping grain.
            efficiency = steeping_efficiency
        elif not include_post_boil and self.stage == Stage.FERMENT:
            efficiency = 0.0
        elif not self.mashable:
            # Non-mashable extracts contribute all of their HWE. Let's ignore edge cases where someone
            # adds a non-mashable to the mash or too late in the fermentation stage.
            efficiency = 1.0
        return 1 + 0.001 * self.hwe(efficiency) * self.kg / volume

    def emcu(self, volume: float) -> float:
        """Return expected color contribution in EMCU given post-boil volume in litres."""
        return self.kg * self.deg_ebc / volume

    @staticmethod
    def percent_extract_to_hwe(percent_extract: float) -> float:
        """Tool to convert %Extract to hot water extract (liter degrees per kilogram).

        %Extract is a common unit in malt datasheets.
        """
        return percent_extract * 0.01 * Fermentable.SUCROSE.hwe

    @staticmethod
    def ppg_to_hwe(ppg: float) -> float:
        """Tool to convert points/pound/gallon to liter*degrees/kg."""
        # points/pound/gallon = gallon*degrees/pound
        # gallon = 3.78541178 l, pound = 0.45359237 kg
        return ppg * 3.78541178 / 0.45359237

    @staticmethod
    def hwe_to_ppg(hwe: float) -> float:
        """Tool to convert liter*degrees/kg to points/pound/gallon."""
        # See Extract.ppg_to_hwe()
        return hwe * 0.45359237 / 3.78541178
