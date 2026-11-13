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
import matplotlib.pyplot as plt
import pandas as pd

from pixels import PixelsError
#from pixels.behaviours import Behaviour

#from common_utils import file_utils
from vision_in_darkness.base import (Conditions, Worlds, Visibilities, Outcomes,
                                     BaseMeta)
from vision_in_darkness.configs import *
from vision_in_darkness.metrics import lick_error
from vision_in_darkness.simulation.simulation_configs import *

MISSING_VALUE = 9999

class Trial(BaseMeta):
    def __init__(self, meta_dir, data=None, name=None, condition=None):
        super().__init__(meta_dir, name)
        self.data = data
        self.condition = condition


    @classmethod
    def get_vr_trial(cls, meta_dir, data=None, name=None, condition=None):
        return cls(meta_dir=meta_dir, data=data, name=name, condition=condition)


    def _process_reward_info(self):
        def _map_old_mice():
            logging.info(
                f"\n> {self.name} is from older cohort, trial {self.id} "
                "is not a punished, but an aborted trial."
            )

            # not punished
            self.punished = False
            # add self.reward_type
            if self.condition == Conditions.LIGHT.name.lower():
                self.reward_type = Outcomes.ABORTED_LIGHT
            elif self.condition == Conditions.DARK.name.lower():
                self.reward_type = Outcomes.ABORTED_DARK
            return None

        # get reward type
        reward_types = self.data.reward_type.unique().astype(int)

        try:
            # Save non-zero reward type
            self.reward_type = reward_types[
                reward_types != Outcomes.NONE].astype(int)[0]
            # not punished
            self.punished = False

        except IndexError:
            if "WDAN" in self.name and \
                self.positions.max() >= self.reward_zone_start:
                _map_old_mice()
            else:
                # no non zero reward type, trial punished
                self.reward_type = reward_types[0]
                # make sure punished trial ends before reward zone
                assert self.positions.max() < self.reward_zone_start
                # punished trial
                self.punished = True

        if not self.punished and (self.reward_type > Outcomes.NONE):
            # Get reward dispensed positions for non-punished & non-missed
            reward_dispensed = self.data.reward_type > Outcomes.NONE
            self.reward_dispense = self.positions[reward_dispensed].iloc[0]
        else:
            # no reward dispense
            self.reward_dispense = np.nan

        return self.reward_type, self.punished, self.reward_dispense


    def extract_metrics(self, trial_id):
        """
        Extract metrics from trial data.

        params
        ===
        trial_id: int, id of trial.

        return
        ===
        metrics: np array, shape (2, 12).
        """
        self.id = trial_id

        # save trial performance metrics and chance levels
        metrics = np.full(
            (len(tr_metrics_maps), len(tr_metrics_maps[0])),
            np.nan,
        )

        # save trial id
        metrics[0, 0] = self.id

        # all non-nan positions of current trial
        self.positions = self.data.position_in_tunnel.astype(int)

        # get reward info
        self._process_reward_info()

        # punished bool
        metrics[0, 1] = self.punished
        # reward type
        metrics[0, 2] = self.reward_type
        # reward triggered/dispensed location
        metrics[0, 5] = self.reward_dispense

        # get starting position safely, esp. when starting positions have
        # interval > 1
        # interval of random selection when choosing starting position (cm)
        rand_start_int = int(self.meta_item("rand_start_int"))
        if rand_start_int == MISSING_VALUE:
            # from old scripts
            assert "WDAN" in self.name
            rand_start_int = 10
        self.start_pos = self.positions[
            [list(map(lambda x: x % rand_start_int, self.positions)).index(0)]
            [0]
        ]

        # trial tunnel length if not punished
        metrics[0, 3] = self.tunnel_reset - self.start_pos

        # find max possible error
        self.max_error = max(
            abs(self.reward_zone_start - self.start_pos),
            abs(self.reward_zone_end - self.tunnel_reset),
        )

        # count & save of all licks
        self.all_licks = self.data.lick_count.astype(int)

        if self.all_licks.sum() < 1:
            logging.info(
                f"\n> No licks detected in current run, next run."
            )
            return metrics

        # locations of all licks
        self.licked_locs = np.repeat(
            self.positions[self.all_licks > 0],
            self.all_licks[self.all_licks > 0],
        )

        # counts of early licks, before reward zone
        self.early_lick_locs = self.licked_locs[
            self.licked_locs < self.reward_zone_start
        ]
        # calculate early error
        self.early_error = lick_error.mean_absolute(
            ref_point=self.reward_zone_start,
            wrong_lick_locs=self.early_lick_locs,
        )

        # get positions of licks too early
        self.too_early_locs = self.early_lick_locs[self.early_lick_locs\
                                                    < self.punish_end]
        # lenience licks
        self.leni_lick_locs = self.early_lick_locs[
            ~self.early_lick_locs.isin(self.too_early_locs)
        ]
        # count of lenience licks
        self.leni_licks = self.leni_lick_locs.size
        metrics[0, 9] = self.leni_licks

        # >>> non punished trials >>>
        if not self.punished:
            # >>> valve opened trials >>>
            if self.reward_type > Outcomes.NONE:
                output = self._process_succeeded_licks()
            # <<< valve opened trials <<<
            # >>> aborted trials >>>
            elif self.reward_type < Outcomes.NONE:
                output = self._process_aborted_licks()
            # <<< aborted trials <<<
        # <<< non punished trials <<<
        # >>> punished trials >>>
        else:
            output = self._process_punished_licks()
        # <<< punished trials <<<

        # extract attributes
        (self.counted_licks, self.wrong_licks, self.error, self.error_index,
         self.water_licks, self.average_licked) = output

        # save average licked position
        metrics[0, 4] = self.average_licked
        # save number of good licks
        metrics[0, 6] = self.counted_licks
        # save number of wrong licks
        metrics[0, 7] = self.wrong_licks
        # save number of water licks
        metrics[0, 8] = self.water_licks
        # save lick error
        metrics[0, 10] = self.error
        # save error index
        metrics[0, 11] = self.error_index

        if np.isnan(self.counted_licks):
            metrics[1, :] = np.nan
        else:
            # get trial chance levels
            self.LE_z, self.chance = self.get_trial_chance()
            metrics[1, :] = self.chance
            # save robust z score
            metrics[0, -1] = self.LE_z

        logging.info(f"\n\t> Metrics\
            \n\treward type\tcounted licks\taverage licked\tlick error"
            "\tlick error z\terror index"
            f"\n\t{int(metrics[0, 2])}\t\t{int(metrics[0, 6])}"
            f"\t\t{metrics[0, 4]:.3f}\t\t{metrics[0, 10]:.3f}"
          f"\t\t{metrics[0, -1]:.3f}\t\t{metrics[0, 11]:.3f}.\n"
        )

        return metrics


    def _process_punished_licks(self):
        """
        Process a punished trial, in which the animal licked too much before the
        reward zone.
        """
        # total number of licks, all licks are early and wrong
        counted_licks = wrong_licks = self.licked_locs.size
        # calculate early error
        error = self.early_error
        # get error index, i.e., normalised error
        error_index = lick_error.error_index(error, self.max_error)
        # no water licks
        water_licks = np.nan
        # get average licked position
        average_licked = self.licked_locs.mean()

        # no water licks to remove but save it anyways
        self.data["lick_count_no_water"] = self.all_licks

        return (counted_licks, wrong_licks, error, error_index, water_licks,
                average_licked)


    def _process_aborted_licks(self):
        """
        Process an aborted trial, in which the animal did not lick in the reward
        zone, but ran passed it.
        All licks are wrong
        """
        # get average licked position
        average_licked = self.licked_locs.mean()
        # all licks, early or late, are wrong
        wrong_licks = self.licked_locs.size

        # counts of late wrong licks, after reward zone ends
        self.late_lick_locs = self.licked_locs[
            self.licked_locs > self.reward_zone_end
        ]

        # get lick error of late licks
        self.late_error = lick_error.mean_absolute(
            ref_point=self.reward_zone_end,
            wrong_lick_locs=self.late_lick_locs,
        )

        # number of off licks
        offs = self.early_lick_locs.size + self.late_lick_locs.size

        # average early & late lick error
        error = (self.early_error * self.early_lick_locs.size\
                    + self.late_error * self.late_lick_locs.size)\
                / offs

        # get error index, i.e., normalised error
        error_index = lick_error.error_index(error, self.max_error)

        # total number of licks
        counted_licks = self.all_licks.sum()
        # no water licks
        water_licks = np.nan

        # no water licks to remove but save it anyways
        self.data["lick_count_no_water"] = self.all_licks

        return (counted_licks, wrong_licks, error, error_index, water_licks,
                average_licked)


    def _process_succeeded_licks(self):
        """
        Process a succeeded trial, in which the animal got a water reward,
        either triggered or given.
        """
        # create included licks, starts by copy all_licks
        included_licks = self.all_licks.copy()

        # lick error is early error
        error = self.early_error

        # get error index, i.e., normalised error
        error_index = lick_error.error_index(error, self.max_error)

        # get positions of licks too early
        too_early_locs = self.early_lick_locs[self.early_lick_locs\
                                            < self.punish_end]

        # NOTE by setting, valve opened in this trial

        # only too early licks are wrong
        wrong_licks = too_early_locs.size

        # get licked locs from dispense onwards
        dispense_onwards = self.licked_locs[self.licked_locs >= self.reward_dispense]

        # double check if there are multiple licks at dispensed location, if
        # so, only the first is trigger, the ones after are water licks 
        n_licks_at_dispense = included_licks[
            self.positions == self.reward_dispense].iloc[0]
        # save water-induced licks to see motivation of the animal,
        # which is number of licks from dispense, but remove the ONE
        # trigger lick at dispense, if any
        if n_licks_at_dispense >= 1:
            water_licks = dispense_onwards.size - 1
            included_licks[self.positions == self.reward_dispense] = 1
        else:
            # allows water licks to be 0, in case animal is not consuming
            water_licks = dispense_onwards.size

        # assign lick count after reward dispense to be 0 to remove licks
        # caused by water droplet
        included_licks[self.positions > self.reward_dispense] = 0
        # remove water licks in trial data
        self.data["lick_count_no_water"] = included_licks

        # for auto-rewarded trials, no licks
        if included_licks.sum() < 1 and self.reward_type > Outcomes.TRIGGERED:
            # if no licks in trials with auto-dispensed water, their lick
            # error is nan, not 0
            counted_licks = 0
            error = np.nan
            error_index = np.nan
            average_licked = np.nan
            logging.info(
                "\n> All licks were caused by reward dispense. Next trial."
            )
            return (counted_licks, wrong_licks, error, error_index, water_licks,
                    average_licked)

        # get postions of included licks
        included_lick_locs = np.repeat(
            self.positions[included_licks > 0],
            included_licks[included_licks > 0],
        )
        # position of average licks, including the trigger lick
        average_licked = included_lick_locs.mean()

        # total number of licks, before reward
        counted_licks = included_licks.sum()

        return (counted_licks, wrong_licks, error, error_index, water_licks,
                average_licked)


    def get_random_sample_metrics(self, positions, lick_sum):
        """
        Getting chance metrics from a random sample.

        params
        ===
        positions: np array, positions along the tunnel.

        lick_sum: int, sum of wrong licks within a trial. 

        occupancy: int or None, total position count.

        return
        ===
        metrics: np array, [punished, reward_triggered, average_licked,
            to_average_lick, errors, wrong licks, logi_curve_params(5 params in
            total)]
        """
        # licked position
        licked = np.full(lick_sum, np.nan)

        # lick and position count
        lick_count = np.full(self.tunnel_reset+1, np.nan, dtype=np.float16)
        position_count = np.full(self.tunnel_reset+1, np.nan, dtype=np.float16)

        # extracted parameters
        metrics = np.full(
            len(random_lick_metrics_map),
            np.nan,
            dtype=np.float16,
        )

        # default punished & reward_triggered flag
        metrics[:2] = 0

        # save starting position for easier results mapping
        metrics[-1] = positions[0]

        # initiate random number generator
        rng = np.random.default_rng()

        # get random sample, and allow replacement
        sample = rng.choice(a=positions, size=lick_sum, axis=0, replace=True)

        # get number of too early licks
        too_early_locs = sample[sample < self.punish_end]

        # flag sample trial being punished
        if too_early_locs.size >= self.punish_threshold:
            punished = 1
            metrics[0] = punished
            reward_dispense = np.nan
            # rest of licks will be discarded since there will be punishment
            too_early_locs.sort()
            sample = too_early_locs[:10]

            # cut position at the last lick
            positions = positions[positions <= sample.max()]

        else:
            # number of random licks within reward zone
            in_zone = sample[
                (sample >= self.reward_zone_start)
                & (sample <= self.reward_zone_end)
            ]

            if in_zone.size >= 1:
                metrics[1] = Outcomes.TRIGGERED
                reward_dispense = in_zone.min()

                # remove extra licks after "reward dispensed"
                sample = sample[sample <= reward_dispense]
            else:
                # aborted trial, missed the zone, no reward dispense
                reward_dispense = np.nan

        # sort sample
        sample.sort()
        # save sample to licked positions
        licked[:sample.size] = sample

        # position of average lick, including the trigger lick
        average_licked = np.mean(sample)
        metrics[2] = average_licked

        # get lick counts at each position
        pos_start = positions.min()
        pos_end = positions.max() + 1
        lick_bin_count = np.bincount(
            sample,
            minlength=pos_end,
        )
        # make sure lick count and current trial positions have the same shape
        lick_bin_count = lick_bin_count[pos_start:]
        lick_count[pos_start:pos_end] = lick_bin_count
        # get position counts at each position
        # NOTE: apr 3 2026 here we use a flat spatial distribution, a better way
        # to do it is to get average running speed, calculate average time
        # needed for each trial length, get number of frames, then randomly
        # sample positions from trial length to simulate occupancy.
        position_count[pos_start:pos_end] = 1

        # get number of too early, early licks, & late licks
        early_lick_locs = sample[sample < self.reward_zone_start]
        late_lick_locs = sample[sample > self.reward_zone_end]
        # total wrong licks
        wrongs = too_early_locs.size + late_lick_locs.size
        # total off licks, i.e., wrong & lenient licks
        offs = early_lick_locs.size + late_lick_locs.size 
        # save number of wrong licks
        metrics[3] = wrongs

        # number of lenience lick
        in_leni = early_lick_locs[~np.isin(early_lick_locs, too_early_locs)]
        metrics[4] = in_leni.size

        # make sure only calculate lick error if there are wrong or lenient
        # licks
        if offs == 0:
            errors = 0
        else:
            # lick errors of early licks
            early_error = lick_error.mean_absolute(
                ref_point=self.reward_zone_start,
                wrong_lick_locs=early_lick_locs,
            )
            # lick error of late licks
            late_error = lick_error.mean_absolute(
                ref_point=self.reward_zone_end,
                wrong_lick_locs=late_lick_locs,
            )

            # average early & late lick error
            #if early_error + late_error <= 1:
            #    mean_error = 0
            #else:
            mean_error = (early_error * early_lick_locs.size\
                        + late_error * late_lick_locs.size)\
                        / offs
            errors = mean_error

        # save lick error
        metrics[5] = errors

        # get max error
        max_error = max(
            abs(self.reward_zone_start - positions[0]),
            abs(self.reward_zone_end - positions[-1]),
        )
        # save error index
        metrics[6] = lick_error.error_index(errors, max_error)

        return (licked, metrics, position_count, lick_count)


    def get_trial_chance(self):
        """
        Access trials simulation results, and get the metrics.
        """
        MIN_LICK = 1
        MAX_LICK = 100
        idx = self.counted_licks - 1

        if self.counted_licks >= MIN_LICK:
            # set it to max_lick if too many licks cuz p_hit will be 0 anyways
            if self.counted_licks > MAX_LICK:
                idx = MAX_LICK - 1
            return self._fetch_chance(idx, MIN_LICK, MAX_LICK)

        elif self.counted_licks < MIN_LICK:
            # 0 lick will give nan metrics
            chance = np.full(len(chance_map), np.nan)
            # p_punished and p_hit is 0
            chance[:2] = 0
            LE_z = np.nan
            logging.info(f"\n> no licks made, all chance metrics are nan.")
            return LE_z, chance 


    def _fetch_chance(self, idx, MIN_LICK, MAX_LICK):
        # TODO apr 23 2026
        # simulate till probs of hit becomes 0, at 100 licks hit probs at 0.0003

        (simulation_cache_dir, licks_shape, metrics_shape,
         compiled_metrics_shape, LE_rank_shape, position_shape, _, _,) =\
        get_sim_configs(MIN_LICK, MAX_LICK)

        # load average simulation metrics of all runs with memory map
        compiled_metrics = file_utils.init_memmap(
            path=simulation_cache_dir/"compiled_metrics.dat",
            shape=compiled_metrics_shape,
            dtype=datatype,
            readonly=True, # read-only
        )
        sim_metrics = compiled_metrics[idx, self.start_pos, :]
        # convert to df
        self.sim_metrics = pd.DataFrame(sim_metrics).T
        self.sim_metrics.columns = compiled_metrics_map
        # calculate robust z score of lick error
        LE_z = ((self.error - self.sim_metrics.LE_median)\
                        / self.sim_metrics.LE_MAD).values[0]

        # get lick error rank
        LE_rank = file_utils.init_memmap(
            path=simulation_cache_dir/"LE_rank.dat",
            shape=LE_rank_shape, # number of simulation
            dtype=datatype,
            readonly=True, # read-only
        )
        # get ranks from all simulations
        ranks = LE_rank[idx, self.start_pos, :]

        # load all simulation metrics of all runs with memory map
        metrics = file_utils.init_memmap(
            path=simulation_cache_dir/"metrics.dat",
            shape=metrics_shape,
            dtype=datatype,
            readonly=True, # read-only
        )
        # get lick error from all runs
        errors = metrics[idx, self.start_pos, :, 5]
        # get rank of current trial lick error in population
        self.LE_rank = ranks[np.abs(self.error - errors).argmin()]
        # get percentile of current trial lick error in population
        self.LE_q = 100 * (self.LE_rank / errors.size)

        # >>> estimate p value of current trial lick error >>>
        # NOTE: with 10000 samples, percentile and estimated p value will be the
        # same, or extremely close
        # get lick error robust z scores from all runs
        LE_robust_z = file_utils.init_memmap(
            path=simulation_cache_dir/"LE_robust_z.dat",
            shape=LE_rank_shape, # number of simulation
            dtype=datatype,
            readonly=True, # read-only
        )
        Zs = LE_robust_z[idx, self.start_pos, :]
        # count number of observations below 
        self.LE_p = np.count_nonzero(Zs < LE_z) / Zs.size
        # for alpha = 0.01 or 0.05, get corresponding critical z scores 
        criticals = np.percentile(Zs, [0.1, 1, 5])
        # <<< estimate p value of current trial lick error <<<

        logging.info(f"\n\t> Chance\
            \n\tprob. of punish\tprob. of hit\tlick error\terror index"
            "\tlick error z 0.05"
            f"\n\t{sim_metrics[0]:.3f}\t\t{sim_metrics[1]:.3f}"
            f"\t\t{sim_metrics[-2]:.3f}\t\t{sim_metrics[-1]:.3f}"
            f"\t\t{criticals[-1]:.3f}.\n"
        )

        # save chance metrics
        chance = np.concatenate(
            [sim_metrics, [self.LE_q, self.LE_p], criticals],
        )
        
        return LE_z, chance
