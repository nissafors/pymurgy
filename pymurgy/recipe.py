from __future__ import annotations

# fmt: off
# Make sure we can always import from ./ no matter where we're called from
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
# fmt: on

import json, inspect
import common
from typing import Any
from hop import Hop
from extract import Extract
from yeast import Yeast
from co2 import CO2
from brewhouse import Brewhouse


class Recipe(common.Serializable):
    """Represents a beer recipe.

    Properties:
        name (str): The name of the recipe.
        brewhouse (Brewhouse): Brewhouse parameters.
        extracts (list[Extract]): Extract givers.
        hops (list[Hop]): Hops.
        yeast (Yeast): Yeast.
        co2 (CO2): Carbonation level.
        mash_time (int): Mash time in minutes.
        mash_temp (int): Mash temperature in degrees Celsius.
        boil_time (int): Boil time in minutes.
        post_boil_volume (int): Post boil volume in litres.
        pitch_temp (int): Pitch temperature in degrees Celsius.
    """

    def __init__(
        self,
        name: str,
        brewhouse: Brewhouse,
        extracts: list[Extract],
        hops: list[Hop],
        yeast: Yeast,
        co2: CO2,
        mash_time: int,
        mash_temp: int,
        boil_time: int,
        post_boil_volume: int,
        pitch_temp: int,
    ):
        """Initialize a new Recipe object."""
        self.name = name
        self.brewhouse = brewhouse
        self.extracts = extracts
        self.hops = hops
        self.yeast = yeast
        self.co2 = co2
        self.mash_time = mash_time
        self.mash_temp = mash_temp
        self.boil_time = boil_time
        self.post_boil_volume = post_boil_volume
        self.pitch_temp = pitch_temp

    def pre_boil_volume(self) -> float:
        """Returns pre-boil volume."""
        boil_hours = self.boil_time / 60.0
        return self.post_boil_volume / ((1 - self.brewhouse.boil_off_rate) ** boil_hours)

    def og(self) -> float:
        """Return original gravity.

        This is different from post_boil_gravity() in the sense that it includes sugar additions to the fermenter.
        """
        return sum([x.sg(self.post_boil_volume, self.brewhouse.efficiency, True) - 1 for x in self.extracts]) + 1

    def post_boil_gravity(self) -> float:
        """Return post-boil gravity.

        This is different from og() in the sense that it excludes sugar additions to the fermenter.
        """
        return sum([x.sg(self.post_boil_volume, self.brewhouse.efficiency, False) - 1 for x in self.extracts]) + 1

    def bg(self) -> float:
        """Returns pre-boil gravity."""
        return (self.post_boil_gravity() - 1) * self.post_boil_volume / self.pre_boil_volume() + 1

    def fg(self) -> float:
        """Returns final gravity."""
        return self.og() - self.attenuation() * (self.og() - 1)

    def attenuation(self) -> float:
        """Returns expected attenuation based on Yeast attenuation and fermentability of extracts."""
        sum_kg = sum([x.kg for x in self.extracts])
        attenuation = 0.0
        for extract in self.extracts:
            if not extract.mashable and extract.fermentability is not None:
                fermentability = extract.fermentability
            else:
                fermentability = self.yeast.attenuation
            weight = extract.kg / sum_kg
            attenuation += weight * fermentability
        return attenuation

    def abv(self) -> float:
        """Returns ABV calculated from OG and FG."""
        fg = self.fg()
        original_extract = common.to_plato(self.og())
        apparent_extract = common.to_plato(fg)
        q = 0.22 + 0.001 * original_extract
        real_extract = (q * original_extract + apparent_extract) / (1 + q)
        abw = (original_extract - real_extract) / (2.0665 - 0.010665 * original_extract)
        return abw * fg / 0.794

    def deg_ebc(self) -> float:
        """Return beer color in degrees EBC using Morey's formula."""
        return 7.913 * sum([x.emcu(self.post_boil_volume) for x in self.extracts]) ** 0.6859

    def ibu(self) -> float:
        """Return bitternes in IBU."""
        return sum(
            [
                x.ibu(
                    self.bg(),
                    self.post_boil_gravity(),
                    self.post_boil_volume,
                    self.brewhouse.temp_approach,
                    self.pitch_temp,
                    self.brewhouse.cooling_coefficient(),
                )
                for x in self.hops
            ]
        )

    def save(self, filename):
        """Writes recipe to json file."""
        with open(filename, "w") as f:
            f.write(json.dumps(dict(self), sort_keys=True, indent=2))

    def load(self, filename):
        """Loads recipe from json file."""
        with open(filename, "r") as f:
            content = f.read()
        dict_repr = json.loads(content)
        self.from_dict(dict_repr)

    @classmethod
    def from_dict(cls, dict_repr: dict) -> Recipe:
        """Populate self from a dict representation."""
        init_sig = inspect.signature(cls.__init__).parameters
        none_params = [None] * (len(init_sig) - 1)  # Exclude self
        return super().from_dict(dict_repr, *none_params, callback=Recipe.from_dict_callback)

    @staticmethod
    def from_dict_callback(key, value: Any) -> Any:
        if key == "extracts":
            return [Extract.from_dict(x) for x in value]
        elif key == "hops":
            return [Hop.from_dict(x) for x in value]
        elif key == "yeast":
            return Yeast.from_dict(value)
        elif key == "co2":
            return CO2.from_dict(value)
        elif key == "brewhouse":
            return Brewhouse.from_dict(value)
        else:
            return value

    def __iter__(self):
        """Yield string representation (key, value) tuples from instance attributes."""
        for k, v in self.__dict__.items():
            if isinstance(v, list):
                v = [dict(x) for x in v]
            elif isinstance(v, common.Serializable):
                v = dict(v)
            yield k, v
