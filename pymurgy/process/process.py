from __future__ import annotations
from dataclasses import dataclass
from ..abstract import Serializable
from ..util import is_instance_of_name, func_params


@dataclass
class Process(Serializable):
    instructions: str = ""

    @staticmethod
    def from_dict_callback(k, v):
        is_list = isinstance(v, list)
        if is_list:
            is_list_of_dict = isinstance(v[0], dict)
        if is_list and is_list_of_dict:
            dict_keys = set(v[0].keys())
            temp_sig = set(func_params(Temperature.__init__))
        if isinstance(v, dict) and list[v.keys()]:
            return Temperature.from_dict(v)
        elif is_list and is_list_of_dict and dict_keys == temp_sig:
            return [Temperature.from_dict(t) for t in v]
        return v

    @classmethod
    def from_dict(cls, dict_repr: dict) -> Process:
        """Populate self from a dict representation."""
        return super().from_dict(dict_repr, callback=Process.from_dict_callback)

    def __iter__(self):
        """Yield json serializable key/value tuples from instance attributes.

        Subclasses of Process tends to contain Temperature or list[Temperature].
        """
        for k, v in self.__dict__.items():
            if is_instance_of_name(v, "Temperature"):
                yield k, dict(v)
            elif isinstance(v, list) and is_instance_of_name(v[0], "Temperature"):
                yield k, [dict(t) for t in v]
            else:
                yield k, v


@dataclass
class Temperature(Serializable):
    """Represents a temperature or temperature change over a period.

    Properties:
        temp_init (float): The temperature at the start of the period in degrees Celsius.
        temp_final (float): The temperature at the end of the period in degrees Celsius.
        time (int): The length of the period in minutes.
    """

    temp_init: float = 0.0
    temp_final: float = 0.0
    time: int = 0
