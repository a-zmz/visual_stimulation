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
        # TODO nov 11 continue here

