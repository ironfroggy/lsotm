from collections import defaultdict
from dataclasses import dataclass
import math
from random import choice, random, randint
from time import time
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

from systems.floatingnumbers import FloatingNumberSystem
from systems.timer import Timers, delay, repeat, cancel
from systems.renderer import CustomRenderer
from systems.text import Text
from systems.menu import MenuSystem
from systems.particles import ParticleSystem
from systems.scoring import ScoreBoard
from systems.tilemap import TilemapSystem
from systems.unitplacement import MushroomPlacement
from systems import ui

from cloud import CloudSystem

from viking import Viking, VikingSpawn

from constants import COLOR
from events import *


def setup(scene):
    def zoom():
        scene.main_camera.width = 20.1
    delay(1, zoom)


ppb.run(
    setup=setup,
    basic_systems=(CustomRenderer, Updater, EventPoller, SoundController, AssetLoadingSystem),
    systems=[
        MenuSystem,
        Tweening,
        Timers,
        ParticleSystem,
        ScoreBoard,
        CloudSystem,
        VikingSpawn,
        ui.UISystem,
        MushroomPlacement,
        TilemapSystem,
        FloatingNumberSystem,
    ],
    resolution=(1280, 720),
    window_title='🍄Last Stand of the Mushrooms🍄',
    target_frame_rate=60,
)
