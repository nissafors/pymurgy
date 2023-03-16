from __future__ import annotations
import json, inspect
from dataclasses import dataclass, field
from datetime import date
from typing import Any
from .brewhouse import Brewhouse
from .mash import Mash
from ..ingredients.hop import Hop
from ..ingredients.extract import Extract
from ..ingredients.yeast import Yeast
from ..ingredients.co2 import CO2
from ..abstract import Serializable
from ..calc import to_plato
from ..util import is_instance_of_name


@dataclass
class Recipe(Serializable):
    """Represents a beer recipe.

    Args:
        name (str): The name of the recipe.
        brewhouse (Brewhouse): Brewhouse parameters.
        extracts (list[Extract]): Extract givers.
        hops (list[Hop]): Hops.
        yeast (Yeast): Yeast.
        co2 (CO2): Carbonation level.
        mash (Mash): The mash process.
        boil_time (int): Boil time in minutes.
        post_boil_volume (int): Post boil volume in litres.
        pitch_temp (int): Pitch temperature in degrees Celsius.
        authors (list[str]): Author(s) of the recipe. Optional.
        date (date): Date of creation. Optional, None if not set.
        description (str): Description of the recipe. Optional.
    """

    name: str
    brewhouse: Brewhouse
    extracts: list[Extract]
    hops: list[Hop]
    yeast: Yeast
    co2: CO2
    mash: Mash
    boil_time: int
    post_boil_volume: int
    pitch_temp: int
    authors: list[str] = field(default_factory=list)
    date: date = None
    description: str = ""

    def pre_boil_volume(self) -> float:
        """Returns pre-boil volume."""
        boil_hours = self.boil_time / 60.0
        return self.post_boil_volume / ((1 - self.brewhouse.boil_off_rate) ** boil_hours)

    def og(self) -> float:
        """Return original gravity.

        This is different from post_boil_gravity() in the sense that it includes sugar additions to the fermenter.
        """
        return sum([x.sg(self.post_boil_volume, self.mash.efficiency, True) - 1 for x in self.extracts]) + 1

    def post_boil_gravity(self) -> float:
        """Return post-boil gravity.

        This is different from og() in the sense that it excludes sugar additions to the fermenter.
        """
        return sum([x.sg(self.post_boil_volume, self.mash.efficiency, False) - 1 for x in self.extracts]) + 1

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
        original_extract = to_plato(self.og())
        apparent_extract = to_plato(fg)
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
                    self.brewhouse.temp_approach,
                    self.pitch_temp,
                    self.brewhouse.cooling_coefficient(),
                    self.boil_time,
                    self.post_boil_volume,
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
        elif key == "mash":
            return Mash.from_dict(value)
        elif key == "date":
            return date.fromisoformat(value)
        else:
            return value

    def __iter__(self):
        """Yield string representation (key, value) tuples from instance attributes."""
        for k, v in self.__dict__.items():
            if isinstance(v, list) and v and not isinstance(v[0], str):
                v = [dict(x) for x in v]
            elif isinstance(v, date):
                v = v.isoformat()
            else:
                if is_instance_of_name(v, "Serializable"):
                    v = dict(v)
            yield k, v
