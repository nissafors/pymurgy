from __future__ import annotations

# fmt: off
# Make sure we can always import from ./ no matter where we're called from
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
# fmt: on

import enum, math
from typing import Callable, Any
from dataclasses import dataclass


def to_kelvin(celsius: float) -> float:
    """Convert from degrees Celsius to degrees Kelvin."""
    return celsius + 273.15


def to_fahrenheit(celsius: float) -> float:
    """Convert from degrees Celsius to degrees Fahrenheit."""
    return celsius * 1.8 + 32.0


def to_plato(sg) -> float:
    """Convert SG to degrees Plato."""
    return -668.962 + 1262.45 * sg - 776.43 * sg**2 + 182.94 * sg**3


def to_psi(bar: float) -> float:
    """Convert from bar to psi."""
    return bar / 0.06894757293168


def to_bar(bar: float) -> float:
    """Convert from psi to bar."""
    return bar * 0.06894757293168


def to_gallons(litres: float) -> float:
    """Convert from litres to US gallons."""
    return litres / 3.785411784


def to_litres(gallons: float) -> float:
    """Convert from US gallons to litres."""
    return gallons * 3.785411784


def compute_cooling_coefficient(temp_surround: float, temp_target: float, time: float, temp_init: float = 100) -> float:
    """Calculate the cooling constant for a liquid. This can be used to calculate temperature at any time using the
    formula:

        T_t = T_s + (T_0 - T_s) * e^(-t * k)

    Where T_t is temperature at the time t (in minutes after the cooling started), T_s is the surrounding temperature
    and T_0 is the initial temperature.

    Args:
        temp_surround (float): The surrounding temperature (deg C), e.g. the ground water temp for an immersion chiller.
        temp_target (float): The temperature to cool to (deg C).
        time (float): The time (min) it takes to cool from temp_init to temp_target.
        temp_init (float): The initial temperature (deg C).

    Returns:
        float: The cooling coefficient k.
    """
    if temp_target <= temp_surround:
        raise ValueError("Target temperature can not be lower than surrounding temperature")
    # Newtons's formula: T_t = T_s + (T_0 - T_s) * e^(-t * k)
    # ...where T_t is temperature at time, T_s is surrounding temperature, T_0 is initian temperature and t is time.
    # We want to find k, the cooling constant:
    # (T_t - T_s) / (T_0 - T_s) = e^(-t * k)
    # ln((T_t - T_s) / (T_0 - T_s)) = -t * k
    return (1 / -time) * math.log((temp_target - temp_surround) / (temp_init - temp_surround))


def compute_cool_time(
    temp_surround: float,
    temp_target: float,
    cooling_coefficient: float,
    temp_init: float = 100,
) -> float:
    """Calculate the time it takes for a liquid to cool.

    Args:
        temp_surround (float): The surrounding temperature (deg C), e.g. the ground water temp for an immersion chiller.
        temp_target (float): The temperature to cool to (deg C).
        temp_init (float): The initial temperature (deg C).
        cooling_coefficent (float): See compute_cooling_coefficient() for details.

    Returns:
        float: The time in minutes for the liquid to cool from temp_init to temp_target.
    """
    if temp_target <= temp_surround:
        raise ValueError("Target temperature can not be lower than surrounding temperature")
    # Newtons's formula: T_t = T_s + (T_0 - T_s) * e^(-t * k)
    # ...where T_t is temperature at time, T_s is surrounding temperature, T_0 is initian temperature and tk is the
    # cooling coefficient. We want to find t:
    # (T_t - T_s) / (T_0 - T_s) = e^(-t * k)
    # ln((T_t - T_s) / (T_0 - T_s)) = -t * k
    return -1.0 * math.log((temp_target - temp_surround) / (temp_init - temp_surround)) / cooling_coefficient


class ComparableEnum(enum.Enum):
    """Base class for comparable enums."""

    def __eq__(self, __o: enum.Enum) -> bool:
        return self.value == __o.value


class AutoIncrementEnum(enum.Enum):
    """Base class for auto-incrementing enums.

    Assigned value is received in __init__ and can be used for properties, while the actual enumerated value will be
    auto-incremented.
    """

    def __new__(cls, *args) -> AutoIncrementEnum:
        """Use incrementing value instead of assigned."""
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, assigned):
        ...


class Stage(ComparableEnum):
    """Enumerates brew stages."""

    MASH = enum.auto()
    BOIL = enum.auto()
    FERMENT = enum.auto()
    CONDITION = enum.auto()


class BeerFamily(ComparableEnum):
    """Enumerates beer familys."""

    ALE = enum.auto()
    LAGER = enum.auto()
    HYBRID = enum.auto()


class BeerStyle(ComparableEnum, AutoIncrementEnum):
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


class Serializable:
    @classmethod
    def from_dict(
        cls,
        dict_repr: dict,
        *args,
        callback: Callable[[Any, Any], Any] = lambda _, v: v,
        **kwargs,
    ) -> Serializable:
        """Return an Deserializable instance created from a dict representation.

        Args:
            dict_repr (dict): The class' attributes represented as a dictionary.
            *args: Positional arguments to construct a new instance.
            callback (callable): Takes the dictionary's key and value as parameters and returns a value.
            **kwargs: Keyword arguments to construct a new instance
        """
        x = cls(*args, **kwargs)
        for k, v in dict_repr.items():
            try:
                getattr(x, k)
                v = callback(k, v)
                setattr(x, k, v)
            except AttributeError:
                continue
        return x

    def __iter__(self):
        """Yield json serializable key/value tuples from instance attributes."""
        return iter(self.__dict__.items())


@dataclass
class Ingredient(Serializable):
    """Base class for ingredients.

    Properties:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL or FERMENT).
    """

    stage: Stage = Stage.BOIL

    @classmethod
    def from_dict(
        cls,
        dict_repr: dict,
        *args,
        callback=lambda k, v: Stage[v] if k == "stage" else v,
        **kwargs,
    ) -> Serializable:
        """Return an Ingredient instance created from a dict representation.

        Args:
            dict_repr (dict): The class' attributes represented as a dictionary.
            *args: Positional arguments to construct a new instance.
            callback (callable): Takes the dictionary's key and value as parameters and returns a value.
            **kwargs: Keyword arguments to construct a new instance
        """
        return super().from_dict(dict_repr, *args, callback=callback, **kwargs)

    def __iter__(self):
        """Yield json serializable key/value tuples from instance attributes."""
        for k, v in self.__dict__.items():
            if isinstance(v, enum.Enum):
                yield k, v.name
            else:
                yield k, v
