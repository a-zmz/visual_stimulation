"""
Objects that represents metadata from a session.
"""
import re
from pathlib import Path

from enum import IntEnum, auto, unique

import pandas as pd

from common_utils import str_utils

class BaseMeta:
    """
    Base class represents meta from a single session.
    """

    def __init__(self, meta_path, name=None):
        self.name = name

        if isinstance(meta_path, (str, Path)):
            self.meta = self.get_meta(meta_path)
            self.meta_path = meta_path
        else:
            self.meta = meta_path
            self.meta_path = None

        # date
        self.date = self.meta_item("date")
        # bodyweight (g)
        self.bodyweight = float(self.meta_item("bodyweight"))
        # bodyweight / baseline weight ratio (%)
        self.bw_ratio = float(self.meta_item("bodyweight/baseline")) * 100

        # food restriction condition group
        self.condition = self.meta_item("condition")

        # food restriction stage
        self.fr_stage = self.meta_item("fr_stage")
        # food weight (g)
        self.food_weight = FoodWeight.from_str(self.meta_item("food_weight"))
        # recording notes
        self.notes = self.meta_item("notes")


    def meta_item(self, index):
        """
        Allow indexing directly into the metadata.
        """
        try:
            return self.meta.loc[index, :].values[0]
        except KeyError:
            return MISSING_VALUE


    @staticmethod
    def get_meta(meta_path):
        # read meta file
        df = pd.read_csv(
            meta_path,
            sep="\t+",
            engine="python",
            header=None,
        )
        # fill NaN with string
        df = df.fillna("None")
        # drop duplicated rz_start
        df = df.drop_duplicates()

        # use first column as index
        meta = df.set_index(0)
        # remove punctuations in the index and values
        meta[1] = list(map(str_utils.remove_punctuation,
                           meta[1].values.astype(str)))
        meta.index = list(map(str_utils.remove_punctuation, meta.index))
        # remove content after bracket in meta names
        meta.index = list(map(str_utils.remove_bracket, meta.index.values))
        
        return meta

@unique
class StimulusType(IntEnum):
    UNKNOWN = 0
    RETINOTOPY = auto()
    GRATINGS = auto()
    MOVIE = auto()

    @classmethod
    def from_str(cls, value):
        return cls.__members__[value.strip().upper()]


@unique
class ScreenStatus(IntEnum):
    UNKNOWN = 0
    UNIFORM = auto()   # U: uniform
    BLACK = auto()     # b: black screen
    GREY = auto()      # g: gray screen
    STATIC = auto()    # S: stationary grating
    FORWARD = auto()   # F: forward drifting grating
    BACKWARD = auto()  # B: backward drifting grating
    MOVIE = auto()     # M: movie
    END = auto()

    @classmethod
    def from_str(cls, value):
        return cls[value.strip().upper()]

    @classmethod
    def from_abbr(cls, value):
        status_map = {
            "b": cls.BLACK,
            "g": cls.GREY,
            "U": cls.UNIFORM,
            "S": cls.STATIC,
            "F": cls.FORWARD,
            "B": cls.BACKWARD,
            "M": cls.MOVIE,
            "E": cls.END,
        }
        try:
            return status_map[value.strip()]
        except KeyError:
            return cls.UNKNOWN

    @property
    def uniform(self) -> bool:
        return self in (ScreenStatus.GREY, ScreenStatus.BLACK, ScreenStatus.END)

    @property
    def drifting(self) -> bool:
        return self in (ScreenStatus.FORWARD, ScreenStatus.BACKWARD)


@unique
class Retinotopy(IntEnum):
    """
    Each trial should have exactly one trial type, or NONE.

    We have 3 x 4 cubes from top left of screen, 8 orientations between 0 to 315
    with 45 deg interval, 0.04 spatial frequency, 1 temporal frequency.
    """
    NONE = 0

    # Row 1, column 1
    ROW_1_COL_1_ORI_0   = auto()
    ROW_1_COL_1_ORI_45  = auto()
    ROW_1_COL_1_ORI_90  = auto()
    ROW_1_COL_1_ORI_135 = auto()
    ROW_1_COL_1_ORI_180 = auto()
    ROW_1_COL_1_ORI_225 = auto()
    ROW_1_COL_1_ORI_270 = auto()
    ROW_1_COL_1_ORI_315 = auto()

    # Row 1, column 2
    ROW_1_COL_2_ORI_0   = auto()
    ROW_1_COL_2_ORI_45  = auto()
    ROW_1_COL_2_ORI_90  = auto()
    ROW_1_COL_2_ORI_135 = auto()
    ROW_1_COL_2_ORI_180 = auto()
    ROW_1_COL_2_ORI_225 = auto()
    ROW_1_COL_2_ORI_270 = auto()
    ROW_1_COL_2_ORI_315 = auto()

    # Row 1, column 3
    ROW_1_COL_3_ORI_0   = auto()
    ROW_1_COL_3_ORI_45  = auto()
    ROW_1_COL_3_ORI_90  = auto()
    ROW_1_COL_3_ORI_135 = auto()
    ROW_1_COL_3_ORI_180 = auto()
    ROW_1_COL_3_ORI_225 = auto()
    ROW_1_COL_3_ORI_270 = auto()
    ROW_1_COL_3_ORI_315 = auto()

    # Row 1, column 4
    ROW_1_COL_4_ORI_0   = auto()
    ROW_1_COL_4_ORI_45  = auto()
    ROW_1_COL_4_ORI_90  = auto()
    ROW_1_COL_4_ORI_135 = auto()
    ROW_1_COL_4_ORI_180 = auto()
    ROW_1_COL_4_ORI_225 = auto()
    ROW_1_COL_4_ORI_270 = auto()
    ROW_1_COL_4_ORI_315 = auto()

    # Row 2, column 1
    ROW_2_COL_1_ORI_0   = auto()
    ROW_2_COL_1_ORI_45  = auto()
    ROW_2_COL_1_ORI_90  = auto()
    ROW_2_COL_1_ORI_135 = auto()
    ROW_2_COL_1_ORI_180 = auto()
    ROW_2_COL_1_ORI_225 = auto()
    ROW_2_COL_1_ORI_270 = auto()
    ROW_2_COL_1_ORI_315 = auto()

    # Row 2, column 2
    ROW_2_COL_2_ORI_0   = auto()
    ROW_2_COL_2_ORI_45  = auto()
    ROW_2_COL_2_ORI_90  = auto()
    ROW_2_COL_2_ORI_135 = auto()
    ROW_2_COL_2_ORI_180 = auto()
    ROW_2_COL_2_ORI_225 = auto()
    ROW_2_COL_2_ORI_270 = auto()
    ROW_2_COL_2_ORI_315 = auto()

    # Row 2, column 3
    ROW_2_COL_3_ORI_0   = auto()
    ROW_2_COL_3_ORI_45  = auto()
    ROW_2_COL_3_ORI_90  = auto()
    ROW_2_COL_3_ORI_135 = auto()
    ROW_2_COL_3_ORI_180 = auto()
    ROW_2_COL_3_ORI_225 = auto()
    ROW_2_COL_3_ORI_270 = auto()
    ROW_2_COL_3_ORI_315 = auto()

    # Row 2, column 4
    ROW_2_COL_4_ORI_0   = auto()
    ROW_2_COL_4_ORI_45  = auto()
    ROW_2_COL_4_ORI_90  = auto()
    ROW_2_COL_4_ORI_135 = auto()
    ROW_2_COL_4_ORI_180 = auto()
    ROW_2_COL_4_ORI_225 = auto()
    ROW_2_COL_4_ORI_270 = auto()
    ROW_2_COL_4_ORI_315 = auto()

    # Row 3, column 1
    ROW_3_COL_1_ORI_0   = auto()
    ROW_3_COL_1_ORI_45  = auto()
    ROW_3_COL_1_ORI_90  = auto()
    ROW_3_COL_1_ORI_135 = auto()
    ROW_3_COL_1_ORI_180 = auto()
    ROW_3_COL_1_ORI_225 = auto()
    ROW_3_COL_1_ORI_270 = auto()
    ROW_3_COL_1_ORI_315 = auto()

    # Row 3, column 2
    ROW_3_COL_2_ORI_0   = auto()
    ROW_3_COL_2_ORI_45  = auto()
    ROW_3_COL_2_ORI_90  = auto()
    ROW_3_COL_2_ORI_135 = auto()
    ROW_3_COL_2_ORI_180 = auto()
    ROW_3_COL_2_ORI_225 = auto()
    ROW_3_COL_2_ORI_270 = auto()
    ROW_3_COL_2_ORI_315 = auto()

    # Row 3, column 3
    ROW_3_COL_3_ORI_0   = auto()
    ROW_3_COL_3_ORI_45  = auto()
    ROW_3_COL_3_ORI_90  = auto()
    ROW_3_COL_3_ORI_135 = auto()
    ROW_3_COL_3_ORI_180 = auto()
    ROW_3_COL_3_ORI_225 = auto()
    ROW_3_COL_3_ORI_270 = auto()
    ROW_3_COL_3_ORI_315 = auto()

    # Row 3, column 4
    ROW_3_COL_4_ORI_0   = auto()
    ROW_3_COL_4_ORI_45  = auto()
    ROW_3_COL_4_ORI_90  = auto()
    ROW_3_COL_4_ORI_135 = auto()
    ROW_3_COL_4_ORI_180 = auto()
    ROW_3_COL_4_ORI_225 = auto()
    ROW_3_COL_4_ORI_270 = auto()
    ROW_3_COL_4_ORI_315 = auto()

    @classmethod
    def from_params(cls, row, col, ori):
        return cls(f"ROW_{row}_COL_{col}_ORI_{ori}").value

    @property
    def parameters(self):
        """Return (row, column, orientation)."""
        if self == type(self).NONE:
            return None, None, None

        _, row, _, col, _, ori = self.name.split("_")
        return int(row), int(col), int(ori)

    @property
    def row(self):
        return self.parameters[0]

    @property
    def column(self):
        return self.parameters[1]

    @property
    def orientation(self):
        return self.parameters[2]

    @property
    def position(self):
        return self.parameters[:2]


@unique
class DriftingGrating(IntEnum):
    """
    Each trial should have exactly one trial type, or NONE.

    We have 12 orientations with 30 deg interval, and 2 spatial frequencies.
    """
    UNKNOWN = 0

    # Spatial frequency: 0.04 cycles/degree
    ORI_0_SF_004   = auto() # 1
    ORI_30_SF_004  = auto() # 2
    ORI_60_SF_004  = auto() # 3
    ORI_90_SF_004  = auto() # 4
    ORI_120_SF_004 = auto() # 5
    ORI_150_SF_004 = auto() # 6
    ORI_180_SF_004 = auto() # 7
    ORI_210_SF_004 = auto() # 8
    ORI_240_SF_004 = auto() # 9
    ORI_270_SF_004 = auto() # 10
    ORI_300_SF_004 = auto() # 11
    ORI_330_SF_004 = auto() # 12

    # Spatial frequency: 0.16 cycles/degree
    ORI_0_SF_016   = auto() # 13
    ORI_30_SF_016  = auto() # 14
    ORI_60_SF_016  = auto() # 15
    ORI_90_SF_016  = auto() # 16
    ORI_120_SF_016 = auto() # 17
    ORI_150_SF_016 = auto() # 18
    ORI_180_SF_016 = auto() # 19
    ORI_210_SF_016 = auto() # 20
    ORI_240_SF_016 = auto() # 21
    ORI_270_SF_016 = auto() # 22
    ORI_300_SF_016 = auto() # 23
    ORI_330_SF_016 = auto() # 24

    @classmethod
    def from_params(cls, ori, sf):
        try:
            return cls[f"ORI_{ori}_SF_{str(sf).strip()}"]
        except KeyError:
            return cls.UNKNOWN

    @property
    def parameters(self):
        """Return (orientation_degrees, spatial_frequency)."""
        if self == type(self).NONE:
            return None, None

        # Example: "ORI_30_SF_004" -> ["ORI", "30", "SF", "004"]
        _, ori, _, sf = self.name.split("_")

        # Naming convention: 004 means 0.04; 016 means 0.16.
        return int(ori), int(sf) / 100

    @property
    def orientation(self):
        return self.parameters[0]

    @property
    def spatial_frequency(self):
        return self.parameters[1]


@unique
class Movie(IntEnum):
    """
    Each trial should have exactly one trial type, or NONE.

    We have 2 movies, both 60s.
    """
    NONE = 0

    # cage movie
    CAGE = auto() # 1

    # natural movie
    NATURAL = auto() # 2

    @classmethod
    def from_value(cls, value: int) -> str:
        return cls(value).name.lower()


class Stage(IntEnum):
    """
    Food restriction stages class represents stages.

    To map Stages[stage_str.strip().upper()]
    """
    NONE = 0
    PRE_FR = auto()
    FR = auto()
    POST_FR = auto()

    @classmethod
    def get_stage_val(cls, stage: str) -> int:
        return cls[stage.strip().upper()].value

    @classmethod
    def from_value(cls, value):
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            if value.lower() in cls.groups():
                return cls.groups()[value.lower()]

            if value.upper() in cls.__members__:
                return cls[value.upper()]

        raise ValueError(f"Unsupported level: {value}")

    @classmethod
    def from_values(cls, values):
        if isinstance(values, (str, cls)):
            values = [values]

        levels = []
        for level in values:
            parsed = cls.from_value(level)
            if isinstance(parsed, list):
                levels.extend(parsed)
            else:
                levels.append(parsed)

        return levels

    @classmethod
    def parse_session_stage(cls, value):
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            value = value.strip()

            if value.upper() in cls.__members__:
                return cls[value.upper()]

        raise ValueError(f"Unsupported concrete session stage: {value}")


class FoodWeight(IntEnum):
    AD_LIBITUM = 99
    FOOD_REMOVED = 0

    @classmethod
    def to_str(cls, value):
        try:
            return cls(value).name.lower()
        except ValueError:
            return str(value)

    @classmethod
    def from_str(cls, value):
        try:
            return cls.__members__[value.strip().upper()].value
        except ValueError:
            return value


class GratingWaveStyle(IntEnum):
    SQUARE_WAVE = 0
    SINE_WAVE = auto()

    @classmethod
    def from_value(cls, value: int) -> str:
        return cls(value).name.lower()
