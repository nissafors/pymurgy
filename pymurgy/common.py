from __future__ import annotations
import enum
from abstract import ComparableEnum as _ComparableEnum
from abstract import AutoIncrementEnum as _AutoIncrementEnum


class Stage(_ComparableEnum):
    """Enumerates brew stages."""

    MASH = enum.auto()
    BOIL = enum.auto()
    FERMENT = enum.auto()
    CONDITION = enum.auto()


class BeerFamily(_ComparableEnum):
    """Enumerates beer familys."""

    ALE = enum.auto()
    LAGER = enum.auto()
    HYBRID = enum.auto()


class BeerStyle(_ComparableEnum, _AutoIncrementEnum):
    """Enumerates beer styles.

    Properties:
        family (BeerFamily): The beer family that the style belongs to.
    """

    ALE = BeerFamily.ALE
    PALE_ALE = BeerFamily.ALE
    BELGIAN_ALE = BeerFamily.ALE
    SOUR_ALE = BeerFamily.ALE
    WHEAT_BEER = BeerFamily.ALE
    BROWN_ALE = BeerFamily.ALE
    PORTER = BeerFamily.ALE
    STOUT = BeerFamily.ALE
    LAGER = BeerFamily.LAGER
    PALE_LAGER = BeerFamily.LAGER
    DARK_LAGER = BeerFamily.LAGER
    BOCK = BeerFamily.LAGER
    HYBRID = BeerFamily.HYBRID

    def __init__(self, family: BeerFamily):
        """Use assigned value as a property."""
        self._family = family

    @property
    def family(self) -> BeerFamily:
        """Returns the beer family that the style belongs to."""
        return self._family
