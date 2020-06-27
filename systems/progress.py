from dataclasses import dataclass
import typing

import ppb
from ppb.systemslib import System
from ppb.events import *

from controllers.dialog import DialogCtrl, DialogOption
from scenes.worldmap import WorldmapScene
from systems.text import Text
from constants import *
from events import *

from ppb_tween import tween
from ppb_timing import delay


LEVEL_GOALS = [
    'spores',
    'vikings',
    'exit',
]


@dataclass
class LevelGoalReached:
    pass


@dataclass
class LevelGoalLost:
    pass


class ProgressSystem(System):
    """Tracks player progress between levels.

    Handles game save and load events.
    """

    def on_level_loaded(self, ev, signal):
        print("LOAD", ev.number)
        self.level = ev.level
        goal_type = self.level['goal_type']
        if goal_type not in LEVEL_GOALS:
            print(f"Unknown goal_type in level {ev.number}: {goal_type}")
        
        self.goal_reached = False
    
    def on_score_updated(self, ev, signal):
        if not self.goal_reached:
            if self.level['goal_type'] == 'spores':
                if self.level['spore_goal'] <= ev.points:
                    signal(LevelGoalReached())
                    self.goal_reached = True
