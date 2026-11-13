"""
Helper functions that deal with I/O.
"""
import numpy as np
import pandas as pd

from common_utils import file_utils

def construct_meta(mice):
    from common_utils.generic_meta import datastore

    # >>> read relevant files >>> 
    data_path = file_utils.make_path(datastore + "data/behaviour/visual_stim/")
    basic_info_path = data_path / "cache/basic_info.h5"

    if basic_info_path.exsits():
        basic_info = file_utils.read_hdf5(basic_info_path)
    else:
        excel_name = "food_restriction_track.xlsx"
        # load info from excel
        info = pd.read_excel(
            io=data_path/excel_name,
            sheet_name=["bodyweight", "food_weight", "stage"],
            header=0,
            index_col=0,
        )

        # get group info
        group = file_utils.load_yaml(
            data_path/"food_restriction_group.yaml"
        )

        # Map mouse ID -> group
        mouse_to_group = {
            mouse: group_name
            for group_name, mice in group.items()
            for mouse in mice
        }

        for key, df in info.items():
            # convert index to object
            df.index = pd.Index(
                df.index.to_numpy("object"),
                dtype=object,
                name="date",
            )

            # columns become (group, mouse_id)
            df.columns = pd.MultiIndex.from_tuples(
                [(mouse_to_group.get(mouse), mouse) for mouse in df.columns],
                names=["group", "mouse_id"]
            )
            # make sure column is object
            df.columns = df.columns.set_levels([
                pd.Index(level.to_numpy(dtype=object), dtype=object)
                for level in df.columns.levels
            ])

        # get total implant weight
        implant_weight = pd.Series(file_utils.load_yaml(
            data_path/"food_restriction_implant_weights.yaml"
        )).sum()

        # remove implant weight from bodyweigth
        bw = info["bodyweight"] - implant_weight
        info["bodyweight"] = bw

        file_utils.write_hdf5(
            path=basic_info_path,
            df=info,
            format="fixed", # skip compression but keep multiindex
        )

    # <<< read relevant files <<< 

    assert 0
    # TODO nov 13 2026
    # CONTINUE HERE!!

    # get stage info
    stage = info["stage"]

    items = ["mouse_id", "date", "bodyweight", "bodyweight/baseline",
             "food_weight", "fr_stage", "condition", "notes"]
    for mouse_id in mice:
        vals = []
        vals.append(mouse_id)

        # TODO nov 13 2026
        # get baseline bodyweight from txt, and bodyweight from excel

        assert 0
    pd.DataFrame

    return None
