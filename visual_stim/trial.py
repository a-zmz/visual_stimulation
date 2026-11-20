"""
`Trial` module maps trial info.
"""

# NOTE: for event alignment, we align to the first timepoint when the event
# starts, and the last timepoint before the event ends, i.e., think of an event
# as a train of 0s and 1s, we align to the first 1s and the last 1s of a given
# event, except for licks since it could only be on or off per frame.

from __future__ import annotations

import pickle

import numpy as np
import pandas as pd

from visual_stim.base import (StimulusType, Retinotopy, Movie, ScreenStatus,
                              GratingWaveStyle)
from visual_stim.configs import *
from visual_stim.constants import *

class Trial():
    def __init__(self, session_meta, session_date, data_path):
        self.data_path = data_path
        # make it clear the meta is session meta, not trial meta 
        self.session_meta = session_meta


    @classmethod
    def get_trial(cls, session_meta, session_date, data_path):
        return cls(
            session_meta=session_meta,
            session_date=session_date,
            data_path=data_path,
        )


    def extract_data(self, trial_id):
        """
        Extract trial data.

        return
        ===
        metrics: np array, shape (2, 12).
        """
        # get trial name and id
        self.name = self.data_path.stem
        self.id = trial_id

        # get trial metadata
        matches = list(self.data_path.parent.glob(f"{self.name}.txt"))
        if len(matches) == 0:
            raise FileNotFoundError(
                f"> {self.name} does not have metadata."
            )
        elif len(matches) > 1:
            raise ValueError(
                f"Multiple metadata matches for trial {self.name!r}: "
                f"{matches}"
            )
        elif len(matches) == 1:
            self.meta_path = matches[0]

        from scipy.io import loadmat

        # load data from .mat
        mat = loadmat(self.data_path, simplify_cells=True)
        params = mat["par"]
        self.stim_type = params["protocol"]

        # trial meta
        self.grey_time = params["customGreyTime"]
        self.grey_RGB = 150 # between 0-255 colour range
        self.black_time = params["customBlackTime"]
        # how screen is split
        self.n_rows = params["nRows"]
        self.n_cols = params["nCols"]

        # also update session meta
        if not "screen_distance" in self.session_meta.index:
            self.session_meta.loc["screen_distance", 1] = str(params["screenDist"])
            self.session_meta.loc["screen_width", 1] = str(params["screenWidth"])
            # screen resolution
            self.session_meta.loc["screen_x", 1] = str(params["imageSizeX"])
            self.session_meta.loc["screen_y", 1] = str(params["imageSizeY"])

        # get timestamps
        timestamps = mat["data_all"]
        data = pd.DataFrame(timestamps)
        # use more clear column name
        data = data.rename(columns={"type": "status"})

        # get trial length
        trial_length = params["End_time"] - params["Trigger_time"]

        # open metadata
        with open(self.meta_path, "r") as f:
            meta_header = f.readlines()[:3]

        # check if stim type is movie
        is_movie = bool(params["natMovie"])

        end_event = {"time": trial_length, "status": "E"}
        if not is_movie:
            end_event["angle"] = 0

        df = pd.concat([data, pd.DataFrame([end_event])], ignore_index=True)

        # add trial id
        df["trial_id"] = self.id

        if is_movie:
            self.stim_type = StimulusType.from_str("movie").name.lower()
            self.data = self.extract_movie_data(params, df)
        else:
            self.data = self.extract_gratings(params, meta_header, df)

        # create meta
        self.build_meta()

        return self.data, self.meta


    def extract_movie_data(self, params, df):
        # get movie type
        self.movie_type = Movie.from_value(params["movieNum"])
        self.play_duration = params["movieTotalDur"]
        self.movie_file_duration = params["movieDur"]
        self.frame_rate = params["moviefps"]

        # keep original event labels: sync events are not screen-state changes.
        df = df.rename(columns={"status": "event"})

        status_map = {
            "TrialStart": ScreenStatus.BLACK,
            "PreMovieGray": ScreenStatus.GREY,
            "PostMovieGray": ScreenStatus.GREY,
            "PostMovieBlack": ScreenStatus.BLACK, # post movie black start
            "TrialEnd": ScreenStatus.END, # post movie black end
            "E": ScreenStatus.END, # drawing finished
        }

        status = []
        for event in df.event:
            stat = ScreenStatus.from_abbr(event[0])
            name = stat.name.lower()
            if "unknown" in name:
                status.append(status_map[event].name.lower())
            else:
                status.append(name)

        df["status"] = status

        # NOTE the end sync comes from showStimuli.m line 236
        df["sync"] = df["event"].isin(
            ["PreMovieGray", "MovieStartSync", "MovieEndSync", "E"]
        ).astype(int)

        # sort chronionologically cuz event M should happen BEFORE start sync
        df = df.sort_values("time", kind="stable").reset_index(drop=True)

        return df


    def extract_gratings(self, params, meta_header, df):
        # NOTE despite setting static time to 0, they are still displayed for
        # 33.3ms since in MovingGratingStimulus.m we performed three flips that
        # fetches the to-be-displayed image from back buffer, and they takes
        # about two screen refresh intervals at 60Hz, makes it ~33.3ms.

        # get trial attr from parameters in .mat
        self.spatial_frequency = params["spatFreq"]
        self.temporal_frequency = params["cyclesPerSecond"]
        # whether gratings displayed in random order; boolean but use float to
        # control for missing values
        self.random_order = float(params["randomOrder"])
        # boolean but use float to control for missing values
        self.bidirectional = float(params["biDirectional"])
        self.static_time = params["timeStatic"]
        self.drift_time = params["timeDrift"]

        # get trial attr from metadata .txt
        self.grating_style = GratingWaveStyle.from_value(params["stimStyle"])
        # boolean but use float to control for missing values
        self.used_gabor = float(params["gabor"])

        # map stim status
        df["status"] = df["status"].map(
            lambda value: ScreenStatus.from_abbr(value).name.lower()
        )

        # NOTE LIMITATION! nov 17 2026
        # here the timestamp is when stim displayed on screen, arduino sync
        # pulse was sent BEFORE all non-drifting status was displayed, except
        # for end, sync pulse was sent AFTER

        # add sync
        df["sync"] = 0
        not_drifting = [not ScreenStatus.from_str(x).drifting for x in df.status]
        df.loc[not_drifting, "sync"] = 1

        if "retinotopy" in self.stim_type:
            data = self._extract_retinotopy(df, params)
        else:
            data = self._extract_gratings(df, meta_header)

        return data


    def _extract_gratings(self, data, meta_header):
        # get sequence
        sequence = [
            token.strip() for token in
            meta_header[0].split(": ")[1][:-2].split(",")
        ]

        # find numbers
        numbers = [int(x) for x in sequence if x.isdigit()]
        # get number of orientations
        self.n_orientations = len(numbers)

        # find strings
        strings = set([x for x in sequence if not x.isdigit()])

        # expand each orientation into static + forward
        expanded = []
        for token in sequence:
            if token in strings:
                expanded.append(ScreenStatus.from_abbr(token).name.lower())
            else:
                expanded.extend([token, token])

        # add the final end row
        expanded.append(ScreenStatus.END.name.lower())

        # align sequence tokens with the corresponding data rows
        tokens = pd.Series(expanded, index=data.index)
        uniform_idx = data.index[data["status"].eq("uniform")]
        data.loc[uniform_idx, "status"] = tokens.loc[uniform_idx]

        return data


    def _extract_retinotopy(self, data, params):
        # get number of orientations
        self.n_orientations = params["numOrient"]

        # get the position of row and column of each stim
        data["col"] = np.nan
        data["row"] = np.nan

        # each Static event at orientation 0 starts a new position.
        starts = data["status"].eq("static") & data["angle"].eq(0)

        # double check if we have the right number of starts
        assert starts.sum() == self.n_rows * self.n_cols

        # position number (0–11), carried through all events in each block
        position = starts.cumsum() - 1

        data["row"] = (position // self.n_cols).astype(int)
        data["col"] = (position % self.n_cols).astype(int)

        return data


    def build_meta(self):
        exclude = {
            "meta",
            "data",
            "session_meta",
            "data_path",
            "meta_path",
        }

        attributes = {
            key: value
            for key, value in vars(self).items()
            if key not in exclude
            and not key.startswith("_")
            and not callable(value)
        }

        self.meta = pd.Series(attributes, dtype=object, name=self.id)

        return self.meta
