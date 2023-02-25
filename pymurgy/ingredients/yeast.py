import math
from dataclasses import dataclass
from .ingredient import Ingredient
from ..calc import to_plato
from ..common import Stage, BeerStyle, BeerFamily


@dataclass
class Yeast(Ingredient):
    """Represents a yeast.

    Properties:
        stage (Stage): The stage at when the ingredient is added (MASH, BOIL, FERMENT or CONDITION).
        name (str): The name of the yeast.
        description (str): Optional description of the yeast (type, reused etc).
        attenuation (float): Attenuation expressed as a decimal number (0.75 = 75%).
    """

    name: str = ""
    description: str = ""
    attenuation: float = 0.75
    stage: Stage = Stage.FERMENT

    @staticmethod
    def cells_to_pitch(
        volume: int, style: BeerStyle, gravity: float, million_cells_per_ml_per_deg_plato: float = None
    ) -> int:
        """Caclulate number of yeast cells to pitch.

        Args:
            volume (int): Litres of wort.
            style (BeerStyle): The style of the beer.
            gravity (float): The gravity of the beer when the beer is pitched. Example: 1.040.
            million_cells_per_ml_per_deg_plato (float): Optional, default is None. Setting None will result in
                    different values depending gravity and the BeerFamily of the style:

                    Family / Gravity    <= 1.060    > 1.060
                    BeerFamily.ALE:     0.75        1.0
                    BeerFamily.LAGER:   1.5         2.0
                    BeerFamily.HYBRID:  1.0         1.5

                    gravity and style is ignored if million_cells_per_ml_per_deg_plato is not None.

        Returns:
            int: Number of yeast cells to pitch.
        """
        # Rule of thumb is 1 million cells per ml of wort per degree plato. Multiply by 0.75 for ales and 1.5 for
        # lagers, or 1.0 for high gravity ales and 2.0 for high gravity lagers.
        # Source: https://www.brewersfriend.com/2012/11/07/yeast-pitch-rates-explained/
        if million_cells_per_ml_per_deg_plato is not None:
            rate_factor = million_cells_per_ml_per_deg_plato
        elif style.family == BeerFamily.LAGER:
            rate_factor = 1.5 if gravity <= 1.060 else 2.0
        elif style.family == BeerFamily.HYBRID:
            rate_factor = 1.0 if gravity <= 1.060 else 1.5
        elif style.family == BeerFamily.ALE:
            rate_factor = 0.75 if gravity <= 1.060 else 1.0
        else:
            raise TypeError()
        ml_of_wort = volume * 1000
        deg_plato = to_plato(gravity)
        return int(round(1000000 * rate_factor * ml_of_wort * deg_plato))

    @staticmethod
    def grams_of_dry_yeast(number_of_cells: int, billion_cells_per_gram: int = 20) -> float:
        """Calculate the amount of dry yeast needed.

        Args:
            number_of_cells (int): Number of yeast cells to pitch.
            billion_cells_per_gram (int): Cells per gram of dry yeast. Optional, defaults to 20 billion.

        Returns:
            float: Grams of dry yeast needed as a decimal number.
        """
        # http://www.mrmalty.com/pitching.php says 20 billion cells / gram.
        # https://www.brewersfriend.com/yeast-pitch-rate-and-starter-calculator says 10 billion cells / gram.
        return number_of_cells / (billion_cells_per_gram * 1000000000)

    @staticmethod
    def packets_of_liquid_yeast(
        number_of_cells: int,
        days_since_mfg_date: int,
        billion_cells_per_package: int = 100,
    ) -> float:
        """Calculate the number of liquid yeast packs/vials needed.

        Args:
            number_of_cells (int): Number of yeast cells to pitch.
            days_since_mfg_date (int): Age of the pack/vial in days from manufacturing date.
            billion_cells_per_package (int): Cells per pack/vial at the date of manufacture. Optional, defaults to 100 billion.

        Returns:
            float: Number of packs/vials needed as a decimal number.
        """
        viable_cells = Yeast.cells_in_liquid_yeast_package(days_since_mfg_date, billion_cells_per_package)
        return number_of_cells / viable_cells

    @staticmethod
    def litres_of_slurry(number_of_cells: int, billion_cells_per_ml: int = 1) -> float:
        """Calculate the amount of yeast slurry needed.

        Args:
            number_of_cells (int): Number of yeast cells to pitch.
            billion_cells_per_ml (int): Cells per gram of dry yeast. Optional, defaults to 20 billion.

        Returns:
            float: Litres of yeast slurry needed as a decimal number.
        """
        # https://www.brewersfriend.com/yeast-pitch-rate-and-starter-calculator/ says 1 billion cells / ml.
        return number_of_cells / (1000 * billion_cells_per_ml * 1000000000)

    @staticmethod
    def cells_in_liquid_yeast_package(days_since_mfg_date: int, billion_cells_per_package: int = 100) -> float:
        """Calculate the amount of viable cells in a package of liquid yeast.

        Args:
            days_since_mfg_date (int): Age of the pack/vial in days from manufacturing date.
            billion_cells_per_package (int): Cells per pack/vial at the date of manufacture. Optional, defaults to 100 billion.

        Returns:
            float: Number of packs/vials needed as a decimal number.
        """
        # Difficult to find reliable information. Several sources qoute an old FAQ from White Labs stating that the
        # viability is 75-85% one month after date of manufacture, but this doesn't say anything about the rate of
        # decay. The best I could find was this discussion from the Beersmith forum:
        # https://beersmith.com/forum/index.php?threads/yeast-viability-calculation.7584/
        #
        # User mm658:
        #   Production Date    Viability-Jamil    Viability-BeerSmith
        #   Today              96%                96%
        #   1 month ago        75%                75%
        #   2 months ago       53%                59%
        #   3 months ago       32%                46.5%
        #   4 months ago       10%                36.5%
        #   The Mr. Malty calculation bottoms out at 10% and seems to stay at that number for anything older than 4
        #   months (which seems suspect to me).  But in general, he seems to be subtracting 21.5 "percentage points"
        #   per month until reaching the 10% floor.
        #
        # This means the Beersmith formula is: viability% = 0.96 * 0.785^months. There's plenty of debate whether this
        # approach is correct, but it eliminates the need for a artificial limit like Mr. Malty's 10% floor.
        # My personal take is that there are so many other factors at play (storage, transport etc) so for a specific
        # package of yeast it really doesn't matter too much which model we use. Let's go with Beersmith's:
        months = days_since_mfg_date / 30
        viability = 0.96 * 0.785**months
        return int(round(viability * billion_cells_per_package * 1000000000))

    @staticmethod
    def starter(volume: float, billion_cells_inoculated: int) -> int:
        """Calculate number of cells in a yeast starter.

        Note 1: The data used by this calculator was collected from starters with 1.036 og at 21C.
        Note 2: There are no data points below an inoculation rate of 5 (e.g. volume=20, billion_cells_inoculated=100).
                This model handles this by never reporting a growth beyond a factor of 6.

        Args:
            volume (float): Starter volume in litres.
            billion_cells_inoculated (int): Number of cells initially added to the starter in billions.

        Returns:
            int: Expected number of cells when the starter is finished.
        """
        rate = billion_cells_inoculated / volume

        @dataclass
        class TableRow:
            rate: float
            growth: float

        # From Yeast, The practical guide to beer fermentation (C. White, J. Zainasheff).
        # 100 billion cells inoculated, gravity 1.036 and temp 21C. Finished at 1.008.
        # Innoculation rate (million cells/ml) = Cells inoculated (billions) / Starter volume (liters)
        # Growth factor: Total cells at finish (billions) / Cells inoculated (billions)
        yield_table = [
            TableRow(0, 6),  # Looks stupid, but we can't assume growth continues forever. Let's top it off at 6.
            TableRow(100 / 20, 600 / 100),
            TableRow(100 / 8, 400 / 100),
            TableRow(100 / 4, 276 / 100),
            TableRow(100 / 2, 205 / 100),
            TableRow(100 / 1.5, 181 / 100),
            TableRow(100 / 1, 152 / 100),
            TableRow(100 / 0.8, 138 / 100),
            TableRow(100 / 0.5, 112 / 100),
            TableRow(100 / 0.25, 1),  # No data, but we need to bottom out somewhere. 400 seems reasonable.
            TableRow(math.inf, 1),
        ]
        growth_factor = 1
        for i in range(len(yield_table) - 1):
            if rate >= yield_table[i].rate and rate < yield_table[i + 1].rate:
                # Simple linear interpolation between data points
                rate_diff = rate - yield_table[i].rate
                g = yield_table[i + 1].growth - yield_table[i].growth
                r = yield_table[i + 1].rate - yield_table[i].rate
                growth_factor = rate_diff * g / r + yield_table[i].growth
                break
        return int(round(growth_factor * billion_cells_inoculated * 1000000000))
