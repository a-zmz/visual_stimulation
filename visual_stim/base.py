"""
Objects that represents metadata from a session.
"""
import re
from pathlib import Path

from enum import IntFlag, auto, IntEnum, Enum

import pandas as pd

from common_utils import str_utils

class BaseMeta:
    """
    Base class represents meta from a single session.
    """

    def __init__(self, meta_dir, name=None):
        self.name = name

        if isinstance(meta_dir, (str, Path)):
            self.meta = self.get_meta(meta_dir)
            self.meta_dir = meta_dir
        else:
            self.meta = meta_dir
            self.meta_dir = None

        # TODO nov 11 2026 for session meta we want:
        # date, mouse id, bodyweight, food weight, stage, trial_types

        # TODO nov 11 2026 bodyweight and food intake need to be fetched from
        # excel

        # TODO nov 11 2026 we need to concatenate data from all trials, and get
        # their meta too

        # date
        self.date = self.meta_item("date")
        # bodyweight (g)
        self.bodyweight = float(self.meta_item("bodyweight"))
        # bodyweight / baseline weight ratio (%)
        self.bodyweight = float(self.meta_item("bodyweight/baseline")) * 100

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
    def get_meta(meta_dir):
        # read meta file
        df = pd.read_csv(
            meta_dir,
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


class Stages(IntEnum):
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
