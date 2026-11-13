"""
This is a generic configuration script.
"""
import logging
import warnings

from collections import namedtuple

import re

# ignore warnings 
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Configure logging to include a timestamp with seconds
logging.basicConfig(
    level=logging.INFO,
    format='''\n%(asctime)s %(levelname)s: %(message)s\
            \n[in %(filename)s:%(lineno)d]''',
    datefmt='%Y%m%d %H:%M:%S',
)

#logging.info('This is an info message.')
#logging.warning('This is a warning message.')
#logging.error('This is an error message.')

session_metrics_map = {
    "dark_length": int, "dark_visibility": int, "repeat_t_count": int,
    "repeat_count": int, "hit_rate": float, "hit_rate_chance": float,
    "first_hit_count": int, "first_hit_rate": float, "good_LE": float,
    "good_LE_chance": float, "all_LE": float, "all_LE_chance": float, "all_EI":
    float, "all_EI_chance": float, "good_LE_z": float, "good_LE_z_5": float,
    "all_LE_z": float, "all_LE_z_5": float, "good_AL": float, "good_AL_chance":
    float, "all_AL": float, "all_AL_chance": float, "good_max_p_pos_lick": int,
    "all_max_p_pos_lick": int,
}
