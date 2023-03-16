from dataclasses import dataclass, field
from .process import Process, Temperature


@dataclass
class Mash(Process):
    """Represents the mash.

    Args:
        steps (list[Temperature]): Mash steps and optionally temperature changes.
        efficiency (float): Brewhouse efficiency as a decimal number (0.8 = 80%)
        liqour_to_grist_ratio (float): Mash thickness for the first mash step.
        absorption (float): Water absorption capacity of the grain in liters per kg.
        grist_heat_capacity (float): Heat capacity of grist in Joules per gram per degree Celsius. Default: 1.722 (to
                match John Palmer's formula from How to brew).
        displacement (float): Grain displacement factor in liters per kg. Default: 0.67.
    """

    steps: list[Temperature] = field(default_factory=list)
    efficiency: float = 0.75
    liqour_to_grist_ratio: float = 3.0
    absorption: float = 1.0
    grist_heat_capacity: float = 1.722
    displacement: float = 0.67

    def strike_volume(self, grist_weight: float) -> float:
        """Computes the amount of strike water needed to reach liqour-to-grist ratio for the first step.

        Args:
            grist_weight (float): Grist weight in kilograms.

        Returns:
            float: Amount of strike water needed in liters.
        """
        return self.liqour_to_grist_ratio * grist_weight

    def total_volume(self, grist_weight: float, wort_volume: int) -> float:
        """Computes the total amount of water needed to drain given volume of wort from the mash.

        For batch sparging the sparge volume = total volume - strike volume.
        For the "no sparge" method use this method to get the strike volume.

        Args:
            grist_weight (float): Grist weight in kilograms.
            wort_volume (int): Desired wort volume in liters.

        Returns:
            float: Amount of strike water and sparge water needed in liters.
        """
        return wort_volume + grist_weight * self.absorption

    def strike_temp(self, grist_temp: int, grist_weight: float, strike_volume: int) -> float:
        """Computes the strike water temperature needed to reach the initial temperature of the first step.

        Args:
            grist_temp (int): Grist temperature in degrees Celsius.
            grist_weight (float): Grist weight in kilograms.
            strike_volume (int): Amount of strike water in liters.

        Returns:
            float: Strike water temperature in degrees Celsius.
        """
        # Sources: How to brew by John Palmer and https://byo.com/article/managing-mash-thickness/
        # Palmer uses k = 0.41 -> grist heat capacity = 1.722 (heat capacity of water = 4.2 and 0.41 = 1.722 / 4.2).
        t_target = self.steps[0].temp_init
        return (t_target - grist_temp) * self._hc_ratio() * grist_weight / strike_volume + t_target

    def infusion_volume(
        self,
        step: int,
        grist_weight: float,
        strike_volume: int,
        mash_temp: int = None,
        liqour_volume: float = None,
        water_temp: int = 100,
    ) -> float:
        """Computes the amount of water needed to reach initial temperature of given step from the final temperature of
        the previous step.

        Note: If mash_volume is not given the aggregated mash volume for later steps will be estimated by recursively
        computing and summing the infusion volumes of earlier steps. This does not take into account if mash_temp
        and/or mash_volume was set or if water_temp was different for a previous step so calculations will be off in
        those cases. For better estimates, always set mash_temp and mash_volume.

        Args:
            step (int): The step to compute for. Range: 1 to number of steps. ValueError raised if out of range.
            grist_weight (float): Grist weight in kilograms.
            strike_volume (int): Amount of strike water used for initial step in liters.
            mash_temp (int): Actual mash temperature in degrees Celsius. Defaults to the final temperature from the
                    previous step if set to None.
            liqour_volume (float): Amount of water added to the mash so far in liters. Defaults to the sum of strike
                    volume and infusion volume of previous steps if set to None.
            water_temp (int): Infusion water temperature in degrees Celsius. Default: 100.

        Returns:
            float: The amount of infusion water in liters.
        """
        # Source: How to brew by John Palmer
        if step < 1 or step >= len(self.steps):
            raise ValueError
        t_init = mash_temp if mash_temp else self.steps[step - 1].temp_final
        if not liqour_volume:
            liqour_volume = strike_volume
            if step > 1:
                for s in range(step, 1, -1):
                    liqour_volume += self.infusion_volume(s - 1, grist_weight, strike_volume, water_temp=water_temp)
        return self.adjustment_volume(grist_weight, t_init, self.steps[step].temp_init, liqour_volume, water_temp)

    def adjustment_volume(
        self,
        grist_weight: float,
        mash_temp: int,
        target_temp: int,
        mash_volume: float,
        water_temp: int = 100,
    ) -> float:
        """Computes the amount of water needed to adjust to a given target temperature.

        Args:
            grist_weight (float): Grist weight in kilograms.
            mash_temp (int): Current mash temperature in degrees Celsius.
            target_temp (int): Desired mash temperature in degrees Celsius.
            mash_volume (float): Current mash volume in liters.
            water_temp (int): Infusion water temperature in degrees Celsius. Default: 100.

        Returns:
            float: The amount of adjustment water in liters.
        """
        return (target_temp - mash_temp) * (self._hc_ratio() * grist_weight + mash_volume) / (water_temp - target_temp)

    def liqour_volume(self, grist_weight: float, mash_volume: float) -> float:
        """Computes the amount of water in the mash accounting for grain displacement.

        Args:
            grist_weight (float): Grist weight in kilograms.
            mash_volume (float): Total volume of liqour and grist in liters.

        Returns:
            float: Amount of liqour in mash in liters.
        """
        # "Grain occupies about 0.08 gal/lb (0.67 l/lb) when mixed with water" (A Formulation Procedure for No-Sparge
        # and Batch-Sparge Recipes by Ken Schwartz 1998-2002). Note that "l/lb" is a typo, should be "l/kg".
        # https://www.bayareamashers.org/wp-content/uploads/2013/07/nbsparge.pdf
        return mash_volume - grist_weight * self.displacement

    def required_space(self, grist_weight: float, liqour_volume: float) -> float:
        """Computes the mash tun size needed to fit grain and water.

        Args:
            grist_weight (float): Grist weight in kilograms.
            liqour_volume (float): Max amount of liqour that will occupy space in the mash tun in liters.

        Returns:
            float: Total space that grist and liqour will occupy in liters.
        """
        # See above about displacement factor.
        return liqour_volume + grist_weight * self.displacement

    def _hc_ratio(self):
        """Returns the heat capacity of grist divided by heat capacity of water."""
        return self.grist_heat_capacity / 4.2
