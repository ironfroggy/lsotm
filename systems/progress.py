from dataclasses import dataclass
import typing

import ppb
from ppb.systemslib import System

from scenes.worldmap import WorldmapScene
from systems.text import Text
from constants import *
from events import *

from ppb_tween import tween
from ppb_timing import delay


class ProgressSystem(System):
    """Tracks player progress between levels.

    Handles game save and load events.
    """
