from __future__ import annotations
import enum
from dataclasses import dataclass
from abstract import Serializable
from common import Stage


@dataclass
class Ingredient(Serializable):
    """Base class for ingredients.

    Args:
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
