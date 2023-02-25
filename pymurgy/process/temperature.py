from dataclasses import dataclass
from ..abstract import Serializable


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
