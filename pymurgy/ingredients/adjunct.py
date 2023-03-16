from dataclasses import dataclass
from .ingredient import Ingredient


@dataclass
class Adjunct(Ingredient):
    """Represents an adjunct.

    Args:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        name (str): The name of the adjunct.
        description (str): An optional description of the adjunct.
        instructions (str): Instructions on how to prepare and precisely when and how to add the adjunct to the beer.
        kg (float): The amount of the adjunct in kilograms.
    """

    name: str = ""
    description: str = ""
    instructions: str = ""
    kg: float = 0.0
