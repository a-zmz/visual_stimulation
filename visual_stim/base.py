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

        # bodyweight (g)
        self.bodyweight = float(self.meta_item("bodyweight"))
        # bodyweight / baseline weight ratio (%)
        self.bodyweight = float(self.meta_item("bodyweight/baseline")) * 100
        # vr level
        self.vr_level = self.meta_item("level")
        # interval of random starting point that determines number of possible
        # starting positions (cm)
        self.start_int = int(self.meta_item("rand_start_int"))
        # end of starting point, i.e., starting point closest to reset (cm)
        self.start_limit = int(self.meta_item("rand_start_lim"))
        # longest tunnel length, i.e., trial reset point (cm)
        self.tunnel_reset = int(self.meta_item("resetpoint"))
        # reward zone starts (cm)
        self.reward_zone_start = int(self.meta_item("rz_start"))
        # reward zone ends (cm)
        self.reward_zone_end = int(self.meta_item("rz_end"))
        # double check if reward_zone_end make sense, on 2024 aug 22, some
        # sessions that has rz_len in meta instead of rz_end, and from 2024 aug
        # 23, all session meta will have rz_start and rz_len, no rz_end to
        # incoporate remapping setup
        if self.reward_zone_end == MISSING_VALUE:
            self.reward_zone_len = int(self.meta_item("rz_len"))
            self.reward_zone_end = self.reward_zone_len + self.reward_zone_start

        # late reward zone where auto & reinforcements are given (cm)
        self.reward_zone_late = self.reward_zone_start + 25
        # lenience for wrong licks, some sessions do not have it
        self.lenience = int(self.meta_item("wrong_lick_lenience"))
        # punish threshold
        self.punish_threshold = int(self.meta_item("punish_threshold"))
        # position after which licks are no longer wrong
        self.punish_end = self.reward_zone_start - self.lenience
        # length of travelled visible tunnel before dark (cm)
        self.pre_dark_len = int(50)
        # length of dark trial (cm)
        self.dark_len = int(self.meta_item("dark_len"))
        # dark level before WDAN05
        self.dark_level = int(self.meta_item("dark_level"))
        if self.dark_level == MISSING_VALUE:
            # dark level from WDAN05 onwards
            self.dark_level = int(self.meta_item("dark_level_idx"))

        # use old way of mapping dark world index for old mice
        use_old_mapping = (
            self.name and
            any(tag in self.name for tag
                in ("WDAN00", "WDAN01", "WDAN03", "WDAN04"))
        )
        if use_old_mapping and self.dark_level in old_dark_level_mapping:
            level_mapping = old_dark_level_mapping[self.dark_level]
        else:
            level_mapping = dark_level_mapping[self.dark_level]

        self.dark_world_idx, self.vis_level = next(iter(level_mapping.items()))

        if not self.vr_level == MISSING_VALUE:
            # check if is a recording session
            self.is_recording = bool(re.search(
                "recording",
                self.vr_level,
            ))
        else:
            self.is_recording = MISSING_VALUE
            
        # landmarks
        self.landmarks = [60, 110, 130, 190, 210, 270, 290, 350, 370, 430, 450]
        # middle of walls, excluding adjacent 10cm to landmark
        self.mid_walls = [70, 100, 140, 180, 220, 260, 300, 340, 380, 420]


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

