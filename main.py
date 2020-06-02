from collections import defaultdict
from dataclasses import dataclass
import math
from random import choice, random, randint
from time import time, perf_counter
import types
from typing import Tuple

import ppb
from ppb import keycodes as k
from ppb.events import KeyPressed, KeyReleased, PlaySound
from ppb.systemslib import System
from ppb.assetlib import AssetLoadingSystem
from ppb.systems import EventPoller
from ppb.systems import SoundController
from ppb.systems import Updater

from ppb_tween import Tweener, Tweening, tween
from ppb_timing import Timers

from systems.cloud import CloudSystem
from systems.floatingnumbers import FloatingNumberSystem
from systems.renderer import CustomRenderer
from systems.text import Text
from systems.particles import ParticleSystem
from systems import ui

from viking import Viking

from constants import COLOR
from events import *


from scenes.game import GameScene
from scenes.title import TitleScene


class DiagnosticSystem(ppb.systemslib.System):
    last_frame = perf_counter()
    frames = [0.0 for i in range(10)]

    # def on_pre_render(self, ev, signal):
    #     # obj_count = len(list(ev.scene))
    #     cur_frame = perf_counter()
    #     f = (1.0 / (cur_frame - self.last_frame))
    #     self.last_frame = cur_frame
    #     self.frames.append(f)
    #     print(sum(self.frames) / 10.0)
    #     del self.frames[0]


ppb.run(
    starting_scene=TitleScene,
    basic_systems=(CustomRenderer, Updater(0.1), EventPoller, SoundController, AssetLoadingSystem),
    systems=[
        Tweening,
        Timers,
        ParticleSystem,
        CloudSystem,
        ui.UISystem,
        FloatingNumberSystem,
        DiagnosticSystem,
    ],
    resolution=(1280, 720),
    window_title='🍄Last Stand of the Mushrooms🍄',
    target_frame_rate=60,
)
