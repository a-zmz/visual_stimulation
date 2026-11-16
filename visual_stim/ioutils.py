"""
Helper functions that deal with I/O.
"""
import numpy as np
import pandas as pd

from common_utils import file_utils

def get_exp(mouse_ids):
    from pixels import Experiment
    from pixels.behaviours.no_behaviour import NoBehaviour

    from analysis.base import (data_dir, interim_dir, processed_dir,
                               session_date_fmt)
    from analysis.project.food_restricted.fr_base import exclude_date

    exp = Experiment(
        mouse_ids=mouse_ids,
        behaviour=NoBehaviour,
        data_dir=data_dir,
        interim_dir=interim_dir, # interim directory
        processed_dir=processed_dir, # processed directory
        interim1_dir=None,
        interim2_dir=None,
        session_date_fmt=session_date_fmt,
        of_date=None,
        exclude_date=exclude_date,
    )

    return exp


def _read_basic_info(mice, path, basic_info_path, keys, group_map):
    from visual_stim.base import FoodWeight

    if basic_info_path.exists():
        info = {}
        for key in keys:
            info[key] = file_utils.read_hdf5(basic_info_path, key=key)
        return info

    else:
        excel_name = "food_restriction_track.xlsx"
        # load info from excel
        info = pd.read_excel(
            io=path/excel_name,
            sheet_name=keys,
            header=0,
            index_col=0,
        )

        # get total implant weight
        implant_weight = pd.Series(file_utils.load_yaml(
            path/"food_restriction_implant_weights.yaml"
        )).sum()

        # remove implant weight from bodyweigth
        bw = info["bodyweight"] - implant_weight
        info["bodyweight"] = bw

        # convert food weight values to float
        info["food_weight"] = (
            info["food_weight"]
            .replace({
                "x": FoodWeight.FOOD_REMOVED,
                "ad libitum": FoodWeight.AD_LIBITUM,
            })
            .apply(pd.to_numeric, errors="raise")
            .astype("float64")
        )

        for key, df in info.items():
            # convert index to object
            df.index = pd.Index(
                df.index.to_numpy("str"),
                dtype=str,
                name="date",
            )

            # columns become (group, mouse_id)
            df.columns = pd.MultiIndex.from_tuples(
                [(group_map.get(mouse), mouse) for mouse in df.columns],
                names=["group", "mouse_id"]
            )
            # make sure column is object
            df.columns = df.columns.set_levels([
                pd.Index(level.to_numpy(dtype=str), dtype=str)
                for level in df.columns.levels
            ])

        file_utils.write_hdf5(
            path=basic_info_path,
            df=info,
            format="fixed", # hdf layout
        )

    return info


def _construct_meta(mice, raw_path, info):
    meta_items = ["mouse_id", "date", "bodyweight", "bodyweight/baseline",
             "food_weight", "fr_stage", "condition", "notes"]

    meta = pd.DataFrame(
        data=np.full(len(meta_items), np.nan),
        index=meta_items,
    )
    meta.columns = ["value"]
    meta.index.name = "item"

    for mouse in mice:
        exp = get_exp(mouse)
        for session in exp.sessions:
            meta["mouse_id"] = mouse
            meta["date"] = session.date
            meta["bodyweight"] = (
                info["bodyweight"]
                .loc[session.date, pd.IndexSlice[:, mouse]]
            )
            assert 0

        raw_path / mouse_id

        # TODO nov 13 2026
        # get baseline bodyweight from txt, and bodyweight from excel

        assert 0

    return None


def construct_meta(mice):
    from common_utils.generic_meta import datastore

    behaviour_path = file_utils.make_path(
        datastore + "data/behaviour/visual_stim/"
    )
    basic_info_path = behaviour_path / "cache/basic_info.h5"
    info_keys = ["bodyweight", "baseline_ration", "food_weight_gain",
                 "food_weight", "stage"]

    # get group info
    group = file_utils.load_yaml(
        behaviour_path / "food_restriction_group.yaml"
    )

    # map mouse ID -> group
    group_map = {
        mouse: group_name
        for group_name, mice in group.items()
        for mouse in mice
    }

    # >>> read relevant files >>> 
    info = _read_basic_info(mice, behaviour_path, basic_info_path, info_keys,
                            group_map)
    # <<< read relevant files <<< 

    pixels_path = behaviour_path.parent.parent / "npx/raw/"
    _construct_meta(mice, behaviour_path, info, group_map)

    print(f"> Metadata constructed for sessions from {mice}.")

    return None
