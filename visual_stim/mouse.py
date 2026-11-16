"""
Mouse object handles virmen data from training sessions for each mouse.
"""
import time

import os
import re
from pathlib import Path
import pickle
from shutil import copytree
import numpy as np

from common_utils import file_utils

from visual_stim.session import Session
from visual_stim.configs import *
from visual_stim.constants import *

class Mouse:
    """
    This class represents an experimental mouse.

    Attributes
    ==========
    mouse_id: str, optional
        The mouse's ID.

    data: list of Session instances.
        The mouse's training data.
    """

    def __init__(self, mouse_id=None, sessions=None, cache_dir=None):
        """
        All Mouse's attributes are initialised here in the init.

        All attributes can be accessed by vars(Mouse).

        attributes
        ===
        mouse_id: str, mouse id to pass to Mouse instance.

        sessions: list, Session objects.
        """

        self.mouse_id = mouse_id
        self.sessions = sessions
        self.cache_dir = cache_dir
    
    def __str__(self):
        """
        string method of class mouse will be invoked whenever do `print`.
        """
        return f"\n> Handling behaviour training data from {self.mouse_id}.\n"


    def __len__(self):
        """
        Allow querying of the number of training days completed.
        """
        return len(self.data)


    def _get_mouse_dir(raw, interim, backup, mouse_id):
        """
        Copy behaviour data of mouse from raw to backup and interim, and get
        mouse_dir.
        """
        raw = file_utils.make_path(raw)
        interim = file_utils.make_path(interim + "behaviour/visual_stim_data")
        backup = file_utils.make_path(backup + "visual_stim_data")

        # mouse folders
        backup_mouse = backup / f"{mouse_id}"
        interim_mouse = interim / f"{mouse_id}"

        # check if mouse folder exists in backup
        try:
            assert backup_mouse.exists() and backup_mouse.is_dir()
        except:
            os.mkdir(backup / f"{mouse_id}")
            logging.info(f"\n> Created {mouse_id} folder in backup.")

        # check if mouse folder exists in interim
        try:
            assert interim_mouse.exists() and interim_mouse.is_dir()
        except:
            os.mkdir(interim / f"{mouse_id}")
            logging.info(f"\n> Created {mouse_id} folder in interim.")

        # map out sessions in raw
        session_names = sorted(set(map(
            lambda x: x.stem, raw.glob(f"*{mouse_id}")))
        )

        # copy to backup & local interim only if files do not exist
        for name in session_names:
            date = name.split("_")[0]
            data_dir = f"{name}/behaviour/{date}"

            if (raw / data_dir).exists():
                # copy to backup & interim mouse folder
                file_utils.copy_directories(
                    sources=raw/data_dir,
                    dests=[backup_mouse/date, interim_mouse/date],
                )

                # also copy metadata
                matches = sorted(
                    (raw / data_dir).parent.parent.glob(f"*{name}*meta.txt")
                )

                if not matches:
                    raise FileNotFoundError(
                        "\n> No metadata matching found in "
                        f"{(raw / data_dir).parent.parent}"
                    )

                if len(matches) > 1:
                    raise ValueError(
                        f"Multiple metadata matches for session {name!r}: {matches}"
                    )

                file_utils.copy_files(
                    source=matches[0],
                    dests=[backup_mouse/date, interim_mouse/date],
                )

        return interim_mouse


    @classmethod
    def get_mouse_sessions(
        cls, raw, interim, backup, mouse_id, of_date=None, include_stage=None,
        no_dates=None,
    ):
        """
        Initialise Mouse object from training data files.

        params
        ===
        cls: Mouse class.

        raw: str, directory that saves raw behavioural training data.

        interim: str, directory of interim behavioural training data.

        backup: str, directory of backup behavioural training data.

        mouse_id: str, mouse id to pass to Mouse instance.

        fron_date: str, training sessions to include since.
            Default: None.

        include_stage: str or list, stages of training sessions to include.
            Default: None.

        no_dates: list, list of dates to exclude.
        """
        # cache dir
        cache_dir = interim + "behaviour_cache/visual_stim"

        from visual_stim.base import Stages
        if include_stage is not None:
            stages = Stages.from_values(include_stage)
        else:
            stages = list(Stages)

        stage_names = [stage.name.lower() for stage in stages]

        # copy all data from raw to backup and interim, and get mouse_dir
        mouse_dir = cls._get_mouse_dir(raw, interim, backup, mouse_id)

        # map out sessions and use Session obj to get data
        session_dates = sorted(set(
            [ses_dir.name for ses_dir in mouse_dir.iterdir() if ses_dir.is_dir()]
        ))
        logging.info(f"\n> Found {len(session_dates)} sessions from {mouse_id}.")

        # map out sessions date
        if of_date is not None:
            if isinstance(of_date, str):
                date_list = [of_date]
            else:
                date_list = of_date

            # in case there were multiple sessions on that day
            date_bool = np.isin(np.array(session_dates), of_date)
            founds = np.array(session_dates)[date_bool]
            for date in date_list:
                date_struct = time.strptime(date, "%Y%m%d")
                logging.info(f"\n> Getting {mouse_id} sessions from "
                             f"{time.strftime('%Y %B %d', date_struct)}."
                )
            session_dates = founds.tolist()

        sessions = {stage: [] for stage in stage_names}
        removal = []
        # initiate Session class from files
        if len(session_dates) > 0:
            for n, name in enumerate(session_dates):
                session = Session.get_session(
                    mouse_dir=mouse_dir,
                    name=name,
                    cache_dir=cache_dir,
                )

                if no_dates:
                    if any([date in name for date in no_dates]):
                        # exclude if not met
                        removal.append(name)
                        continue

                raw_stage = session.meta_item("fr_stage")
                if raw_stage == MISSING_VALUE:
                    ses_stage = Stages.NONE
                else:
                    ses_stage = Stages.parse_session_stage(raw_stage)

                if not include_stage is None:
                    # only include sessions from certain training stage 
                    at_stage = ses_stage in stages
                else:
                    # if include_stage is None then we include all stages
                    at_stage = True

                # exclude sessions with no data
                if len(os.listdir(session.data_dir)) == 0 or not at_stage:
                    removal.append(name)
                    #logging.warning(f"\n> Excluded session {name}.")
                    continue

                # clean up data
                clean_data = session.concat_raw_data()

                sessions[ses_stage.name.lower()].append(session)

            # remove excluded sessions from names
            session_names = list(
                filter(lambda x: x not in removal, session_names)
            )

            # get collapsed stages map
            collapse_map = Levels.collapse_name_map(stages)
            # group sessions by main stage if all stages from the main stage
            # were included
            grouped_sessions = {}
            for stage, ls in sessions.items():
                key = collapse_map.get(stage, stage)
                # use current stage if not all stages included
                grouped_sessions.setdefault(key, []).extend(ls)

            output_sessions = []
            no_empty = {
                k: v for k, v in grouped_sessions.items() if v
            }
            for stage in no_empty:
                # sort sessions by date
                no_empty[stage].sort(key=lambda s: s.name)

            # sort sessions by name
            output_sessions.sort(key=lambda s: s.name)

            mouse = cls(mouse_id=mouse_id, sessions=output_sessions,
                        cache_dir=cache_dir)

            if len(session_names) == 0:
                raise ValueError(f"Did not find {include_stage} stage sessions "
                    f"from {mouse_id}, class Mouse will be empty.")

            date_start = time.strptime(
                output_sessions[0].name.split("_")[0], "%Y%m%d"
            )
            date_end = time.strptime(
                output_sessions[-1].name.split("_")[0], "%Y%m%d"
            )

            logging.info(
            f"\n> Included {len(output_sessions)} {include_stage} stage"
                f" sessions between {time.strftime('%Y %B %d', date_start)} to"
                f" {time.strftime('%Y %B %d', date_end)}.")
        else:
            raise ValueError(f"{mouse_id} not found, class Mouse will be empty.")

        return mouse


    def get_trials(self):
        """
        Get trials from training sessions of a mouse.

        """
        trials = {}

        for day, session in enumerate(self.sessions):
            trials[session.name] = session.get_trials()

        return trials


    def sync_streams(self, SAMPLE_RATE, sync_idx, ref_idx):
        """
        Sync vr data with neural data from all selected training sessions of a
        mouse.
        """
        synched = {}
        logging.info("\n> Getting upsampled from the most recent "
                    f"{len(self.sessions)} sessions...")

        # NOTE jun 6 2025: synchronisation would happen between two exclusive
        # streams, so it would require sync_idx and ref_idx to be multiple
        # arrays, and the number of arrays be the same as number of sessions
        for day, session in enumerate(self.sessions):
            synched[session.name] = session.sync_streams(
                SAMPLE_RATE,
                sync_idx,
                ref_idx,
            )

        return synched
