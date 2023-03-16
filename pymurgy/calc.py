# fmt: off
# Make sure we can always import from ./ no matter where we're called from
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
# fmt: on
import math


def celsius_to_kelvin(celsius: float) -> float:
    """Convert from degrees Celsius to degrees Kelvin."""
    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert from degrees Celsius to degrees Kelvin."""
    return kelvin - 273.15


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert from degrees Celsius to degrees Fahrenheit."""
    return celsius * 1.8 + 32.0


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert from degrees Fahrenheit to degrees Celsius."""
    return (fahrenheit - 32) * 5 / 9


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


def cooling_coefficient(temp_surround: float, temp_target: float, time: float, temp_init: float = 100) -> float:
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


def cool_time(
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
        cooling_coefficent (float): See cooling_coefficient() for details.

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


def boil_off_rate(pre_boil_volume: float, post_boil_volume: float, boil_time: float) -> float:
    """Compute boil-off rate.

    Args:
        pre_boil_volume (float): Measured pre-boil volume in liters.
        post_boil_volume (float): Measured post-boil volume in liters.
        boil_time (float): Boil time in minutes.

    Returns:
        float: Evaporation rate per hour as a decimal number (e.g. 0.15 = 15%).
    """
    return 1 - (post_boil_volume / pre_boil_volume) ** (1 / (boil_time / 60))
