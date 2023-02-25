from __future__ import annotations
import enum
from typing import Callable, Any


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
