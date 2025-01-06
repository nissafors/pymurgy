from __future__ import annotations
from dataclasses import dataclass, field
from ..abstract import Serializable
from ..calc import cooling_coefficient
from ..ingredients.water import WaterProfile


@dataclass
class Brewhouse(Serializable):
    """Represents The brewhouse.

    Args:
        boil_off_rate (float): The rate of evaporation per hour.
        temp_approach (int): Lower wort temperature limit for the chilling procedure in degrees Celsius.
        temp_target (int): A target wort temperature in degreess Celsius for which the cooling time from boil is known.
        cool_time_boil_to_target (int): The time in minutes it takes to cool the wort from boiling to temp_target.
    """

    boil_off_rate: float = 0.14
    temp_approach: int = 15
    temp_target: int = 20
    cool_time_boil_to_target: int = 30
    water_profile: WaterProfile = field(default_factory=lambda: WaterProfile())

    def cooling_coefficient(self) -> float:
        """Get the cooling coefficient for this brewhouse."""
        return cooling_coefficient(self.temp_approach, self.temp_target, self.cool_time_boil_to_target, 100)

    @staticmethod
    def from_dict_callback(k, v):
        if k == "water_profile":
            return WaterProfile(
                ppm_calcium=v["ppm_calcium"],
                ppm_sodium=v["ppm_sodium"],
                ppm_magnesium=v["ppm_magnesium"],
                ppm_chloride=v["ppm_chloride"],
                ppm_bicarbonate=v["ppm_bicarbonate"],
                ppm_sulfate=v["ppm_sulfate"],
            )
        return v

    @classmethod
    def from_dict(cls, dict_repr: dict) -> Brewhouse:
        """Populate self from a dict representation."""
        return super().from_dict(dict_repr, callback=cls.from_dict_callback)

    def __iter__(self):
        """Yield json serializable key/value tuples from instance attributes."""
        for k, v in self.__dict__.items():
            if isinstance(v, WaterProfile):
                yield k, dict(v)
            else:
                yield k, v
