from pathlib import Path

import pandas as pd
import numpy as np

from common_utils import file_utils

from visual_stim.base import BaseMeta
from visual_stim.configs import *
from visual_stim.trial import Trial

class Session(BaseMeta):
    """
    Represents a single session, mainly its behavioural data.
    """

    def __init__(self, date=None, data_dir=None, meta_path=None, cache_dir=None):
        super().__init__(meta_path, name=date)
        self.cache_dir = cache_dir
        self.data_dir = data_dir
        self.meta_path = meta_path
        self.mouse_id = meta_path.name.split("_")[-2]


    @classmethod
    def get_session(cls, mouse_dir=None, date=None, cache_dir=None):
        """
        Initialise a Session object from behavioural data file.

        params
        ===
        mouse_dir: str, directory to behavioural training data of a session
        from a experimental mouse.
        """
        if mouse_dir is None or date is None:
            raise ValueError("mouse_dir and date must be provided.")

        mouse_dir = Path(mouse_dir)

        if not mouse_dir.is_dir():
            raise NotADirectoryError(
                f"Mouse directory does not exist or is not a directory: {mouse_dir}"
            )

        ses_dir = mouse_dir / date
        matches = sorted(ses_dir.glob(f"*{date}*meta*"))

        if not matches:
            raise FileNotFoundError(
                f"No metadata matching '*{date}*meta*' found in {ses_dir}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"Multiple metadata matches for session {date!r}: {matches}"
            )

        return cls(
            date=date,
            data_dir=ses_dir,
            meta_path=matches[0],
            cache_dir=cache_dir,
        )


    def concat_raw_data(self):
        """
        Write getting trial data as a separate function to deal with .mat file
        so that the same code can be reused.

        return
        ===
        output: 
        """
        # get directories
        data_path = self.cache_dir\
                    + f"trials/{self.mouse_id}_{self.date}_trials.h5"
        meta_path = self.cache_dir\
                    + f"trials/{self.mouse_id}_{self.date}_trial_meta.h5"

        try:
            data = file_utils.read_hdf5(data_path)
            meta = file_utils.read_hdf5(meta_path)
            logging.info(
                f"\n> Concatenated trials of {self.mouse_id} "
                f"{self.date} is loaded."
            )

        except FileNotFoundError:
            logging.warning(
                f"\n> Concatenated trials not found for {self.mouse_id}, "
                   f"{self.date} extract now.")

            data, meta = self._concat_raw_data()
            file_utils.write_hdf5(data_path, data)
            file_utils.write_hdf5(meta_path, meta)

        except (KeyError, ValueError, OSError) as e:
            logging.error(f"\nError loading HDF5 file: {e}")
            raise

        return data, meta


    def _concat_raw_data(self):
        from visual_stim.base import StimulusType
        stim_types = [mem.name.lower() for mem in list(StimulusType)]

        data = dict(zip(stim_types, [[], [], [], []]))
        meta = {}
        for t, trial_path in enumerate(self.trial_paths):
            # initiate trial object
            trial = Trial.get_trial(
                session_meta=self.meta,
                session_date=self.date,
                data_path=trial_path,
            )
            trial_data, trial_meta = trial.extract_data(t)

            data[trial.stim_type].append(trial_data)
            meta[t] = trial_meta

        # concat data and remove empty
        data = {
            key: pd.concat(frames, axis=0)
            for key, frames in data.items()
            if len(frames) > 0
        }

        # concat meta
        meta_df = (
            pd.DataFrame(meta)
            .rename_axis(index="attribute", columns="trial_id")
        ).T
        # recover numeric types where possible
        meta_df = meta_df.infer_objects()

        return data, meta_df

