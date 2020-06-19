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

    def on_mushroom_death(self, ev: MushroomDeath, signal):
        remaining = list(ev.scene.get(tag='mushroom'))
        if not remaining:
            signal(ppb.events.StartScene(WorldmapScene))
