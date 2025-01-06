from __future__ import annotations
from dataclasses import dataclass, field
from .ingredient import Ingredient
from common import Stage
from abstract import Serializable
import enum


class WaterProfile(Serializable):
    """Represents a water profile.

    Source for presets and conversions: How to brew by John Palmer

    Args:
        ppm_calcium (float): Parts per million of Ca+2 ions in the water.
        ppm_sodium (float): Parts per million of Na+ ions in the water.
        ppm_magnesium (float): Parts per million of Mg+2 ions in the water.
        ppm_chloride (float): Parts per million of Cl- ions in the water.
        ppm_bicarbonate (float): Alkalinity as parts per million of HCO3- ions in the water.
        ppm_sulfate (float): Parts per million of SO4-2 ions in the water.

    Read-only properties:
        ppm_calcium (float): Parts per million of Ca+2 ions in the water.
        ppm_sodium (float): Parts per million of Na+ ions in the water.
        ppm_magnesium (float): Parts per million of Mg+2 ions in the water.
        ppm_chloride (float): Parts per million of Cl- ions in the water.
        ppm_bicarbonate (float): Alkalinity as parts per million of HCO3- ions in the water.
        ppm_sulfate (float): Parts per million of SO4-2 ions in the water.
    """

    def __init__(
        self,
        ppm_calcium: float = 0.0,
        ppm_sodium: float = 0.0,
        ppm_magnesium: float = 0.0,
        ppm_chloride: float = 0.0,
        ppm_bicarbonate: float = 0.0,
        ppm_sulfate: float = 0.0,
    ):
        self._ppm_calcium = ppm_calcium
        self._ppm_sodium = ppm_sodium
        self._ppm_magnesium = ppm_magnesium
        self._ppm_chloride = ppm_chloride
        self._ppm_bicarbonate = ppm_bicarbonate
        self._ppm_sulfate = ppm_sulfate

    @classmethod
    def preset_pilsen(cls):
        """Creates a water profile similar to that of Pilsen, useful for pilseners.

        Returns:
            WaterProfile: An object representing the water profile of Pilsen.
        """
        return cls(10, 3, 3, 4, 3, 4)

    @classmethod
    def preset_dublin(cls):
        """Creates a water profile similar to that of Dublin, useful for dry stouts.

        Returns:
            WaterProfile: An object representing the water profile of Dublin.
        """
        return cls(118, 12, 4, 19, 319, 54)

    @classmethod
    def preset_dortmund(cls):
        """Creates a water profile similar to that of Dormund, useful for export lagers.

        Returns:
            WaterProfile: An object representing the water profile of Dortmund.
        """
        return cls(225, 60, 40, 60, 220, 120)

    @classmethod
    def preset_vienna(cls):
        """Creates a water profile similar to that of Vienna, useful for Vienna lagers.

        Returns:
            WaterProfile: An object representing the water profile of Vienna.
        """
        return cls(200, 8, 60, 12, 120, 125)

    @classmethod
    def preset_munich(cls):
        """Creates a water profile similar to that of Munich, useful for oktoberfest beers.

        Returns:
            WaterProfile: An object representing the water profile of Munich.
        """
        return cls(76, 5, 18, 2, 152, 10)

    @classmethod
    def preset_london(cls):
        """Creates a water profile similar to that of London, useful for Brittish bitters.

        Returns:
            WaterProfile: An object representing the water profile of London.
        """
        return cls(52, 86, 32, 34, 104, 32)

    @classmethod
    def preset_edinburgh(cls):
        """Creates a water profile similar to that of Edinburgh, useful for Scottish ales.

        Returns:
            WaterProfile: An object representing the water profile of Edinburgh.
        """
        return cls(125, 55, 25, 65, 225, 140)

    @classmethod
    def preset_burton(cls):
        """Creates a water profile similar to that of Burton-on-Trent, useful for India pale ales.

        Returns:
            WaterProfile: An object representing the water profile of Burton-on-Trent.
        """
        return cls(352, 54, 24, 16, 320, 820)

    @property
    def ppm_calcium(self):
        return self._ppm_calcium

    @property
    def ppm_sodium(self):
        return self._ppm_sodium

    @property
    def ppm_magnesium(self):
        return self._ppm_magnesium

    @property
    def ppm_chloride(self):
        return self._ppm_chloride

    @property
    def ppm_bicarbonate(self):
        return self._ppm_bicarbonate

    @property
    def ppm_sulfate(self):
        return self._ppm_sulfate

    @staticmethod
    def alkalinity_as_cac03_to_ppm_hco0(alkalinity: float) -> float:
        """Convert alkalinity as CaCO3 to HCO3 (ppm).

        Args:
            alkalinity (float): Alkalinity as CaCO3.

        Returns:
            float: Bicarbonate content of water in parts per million.
        """
        return alkalinity * 61 / 50

    @staticmethod
    def ppm_hco0_to_alkalinity_as_cac03(hco3: float) -> float:
        """Convert HCO3 (ppm) to alkalinity as CaCO3.

        Args:
            hco3 (float): Bicarbonate content of water in parts per million.

        Returns:
            float: Alkalinity as CaCO3.
        """
        return hco3 * 50 / 61

    @classmethod
    def from_dict(cls, dict_repr: dict) -> WaterProfile:
        """Populate self from a dict representation."""
        x = cls()
        for k, v in dict_repr.items():
            if hasattr(x, k):
                # WaterProfile only has read-only properties so we must set the corresponding private member instead.
                setattr(x, f"_{k}", v)
        return x

    def __iter__(self):
        """Yield json serializable key/value tuples from instance attributes."""
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                # Include if property, otherwise ignore
                if hasattr(self, k[1:]):
                    yield k[1:], v
            else:
                yield k, v


@dataclass
class SaltAdditions(Ingredient):
    """Represents brewing water.

    Args:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        g_caco3 (float): Chalk additon in grams.
        g_nahco3 (float): Sodium bicarbonate addition in grams.
        g_caso4 (float): Gypsum addition in grams.
        g_cacl2 (float): Calcium chloride addition in grams.
        g_mgso4 (float): Magnesium sulfate addition in grams.
    """

    stage: Stage = field(default_factory=lambda: Stage.MASH)
    g_caco3: float = 0.0
    g_nahco3: float = 0.0
    g_caso4: float = 0.0
    g_cacl2: float = 0.0
    g_mgso4: float = 0.0

    def profile(self, source: WaterProfile, volume: float) -> WaterProfile:
        """Calculate resulting water profile from a source water profile plus salt additions.

        Notes on the HCO3 contribution from CaCO3: from https://www.brunwater.com/articles/carbonate-and-bicarbonate:
        "...in brewing chemistry, there is no chance for carbonate to exist in our water or wort. Any carbonate picks
        up an fxtra hydrogen proton and converts itself into bicarbonate. So, bicarbonate is the ion we should be
        quantifying fhen working with brewing chemistry."
        "The molecular weight of carbonate is 60 grams and bicarbonate is 61 grams. Dividing by their electrical charge
        results in 30 grams per equivalent for carbonate and 61 grams per equivalent for bicarbonate"

        Args:
            source (WaterProfile): Ion contents of source water.
            volume (float): Water volume in litres.

        Returns:
            WaterProfile: An object representing the resulting water profile from source and salt additions.

        Raises:
            ValueError: If volume is negative.
        """
        profile = WaterProfile(
            ppm_calcium=source.ppm_calcium,
            ppm_sodium=source.ppm_sodium,
            ppm_magnesium=source.ppm_magnesium,
            ppm_chloride=source.ppm_chloride,
            ppm_bicarbonate=source.ppm_bicarbonate,
            ppm_sulfate=source.ppm_sulfate,
        )

        if volume == 0:
            return profile
        elif volume < 0:
            raise ValueError("Negative volume not allowed")

        # Chalk addition
        profile._ppm_calcium += self.g_caco3 * 397.5 / volume
        profile._ppm_bicarbonate += self.g_caco3 * (598.1 * 61.0 / 30.0) / volume

        # NaHCO3 addition
        profile._ppm_sodium += self.g_nahco3 * 283.9 / volume
        profile._ppm_bicarbonate += self.g_nahco3 * 723.0 / volume

        # CaSO4 addition
        profile._ppm_calcium += self.g_caso4 * 232.8 / volume
        profile._ppm_sulfate += self.g_caso4 * 558.0 / volume

        # CaCl2 addition
        profile._ppm_calcium += self.g_cacl2 * 272.5 / volume
        profile._ppm_chloride += self.g_cacl2 * 480.7 / volume

        # MgSO4 addition
        profile._ppm_magnesium += self.g_mgso4 * 98.4 / volume
        profile._ppm_sulfate += self.g_mgso4 * 389.9 / volume

        return profile
