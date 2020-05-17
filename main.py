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

from systems.floatingnumbers import FloatingNumberSystem
from systems.timer import Timers, delay, repeat, cancel
from systems.tweening import Tweener, TweenSystem, tween
from systems.renderer import CustomRenderer
from systems.text import Text
from systems.menu import MenuSystem
from systems.particles import ParticleSystem
from systems.scoring import ScoreBoard
from systems import ui

from cloud import CloudSystem
from mushroom import Mushroom, MushroomPlacement
from viking import Viking, VikingSpawn

from constants import COLOR
from events import *


def setup(scene):
    # text = Text("Hello, World", V(0, -4))
    # scene.add(text)

    scene.add(ppb.Sprite(
        image=ppb.Image("resources/BACKGROUND.png"),
        size=12,
        layer=-1,
    ), tags=['bg'])



ppb.run(
    setup=setup,
    basic_systems=(CustomRenderer, Updater, EventPoller, SoundController, AssetLoadingSystem),
    systems=[
        MenuSystem,
        TweenSystem,
        Timers,
        ParticleSystem,
        ScoreBoard,
        CloudSystem,
        VikingSpawn,
        ui.UISystem,
        MushroomPlacement,
        FloatingNumberSystem,
    ],
    resolution=(1280, 720),
    window_title='🍄Last Stand of the Mushrooms🍄',
    target_frame_rate=60,
)
