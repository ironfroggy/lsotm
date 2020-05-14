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

from events import *
from timer import Timers, delay, repeat, cancel
from tweening import Tweener, TweenSystem, tween
from renderer import CustomRenderer
from text import Text
from menu import MenuSystem
import spells

V = ppb.Vector


# Constants

COLOR = {
    'GREEN': (0, 255, 0),
    'RED': (255, 0, 0),
    'DARKRED': (128, 0, 0),
    'YELLOW': (255, 255, 0),
    'BLUE': (0, 0, 255),
    'VIOLET': (255, 128, 255),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'NEARBLACK': (64, 64, 64),
}


def first(iterator):
    return next(iter(iterator))

def proxy_method(attr, name):
    def _(self, *args, **kwargs):
        obj = getattr(self, attr)
        return getattr(obj, name)(*args, **kwargs)
    _.__name__ = name
    return _


@dataclass
class Rect:
    lower: ppb.Vector
    upper: ppb.Vector


@dataclass
class Sparkler:
    position: ppb.Vector
    sparkle_timer = None

    def spark(self, color, area=4.0):
        x = -area/2.0 + random() * area
        y = -area/2.0 + random() * area
        pos = self.position + V(x, y)
        ParticleSystem.spawn(self.position, color, pos)

    def sparkle(self, seconds, color):
        self.start_sparkle(color)
        delay(seconds, self.stop_sparkle)
    
    def start_sparkle(self, color):
        if self.sparkle_timer:
            self.stop_sparkle()
            self.sparkle_timer = repeat(0.01, lambda: self.spark(color))
    
    def stop_sparkle(self):
        if self.sparkle_timer:
            cancel(self.sparkle_timer)
            self.sparkle_timer = None

    def burst(self, duration, color, source=None, target=None):
        if target is None:
            tleft, ttop = -2, 2
            tright, tbottom = 2, -2
        elif isinstance(target, ppb.Vector):
            tleft, ttop = target
            tright, tbottom = target
        else:
            tleft, ttop = target[0]
            tright, tbottom = target[1]

        if source is None:
            sleft, stop = 0, 0
            sright, sbottom = 0, 0
        elif isinstance(source, ppb.Vector):
            sleft, stop = source
            sright, sbottom = source
        else:
            sleft, stop = source[0]
            sright, sbottom = source[1]

        step = duration / 100
        for i in range(int(100 * duration)):
            tx = tleft + random() * (tright - tleft)
            ty = tbottom + random() * (ttop - tbottom)
            sx = sleft + random() * (sright - sleft)
            sy = sbottom + random() * (stop - sbottom)
            spos = self.position + V(sx, sy)
            tpos = self.position + V(tx, ty)
            delay(i * step, lambda spos=spos, tpos=tpos: ParticleSystem.spawn(spos, color, tpos))


class TickSystem(System):
    callbacks = []
    game_started = False
    
    @classmethod
    def call_later(self, seconds, func):
        self.callbacks.append((time() + seconds, func))
    
    @classmethod
    def on_start_game(cls, ev, signal):
        cls.callbacks = []
        cls.game_started = True
    
    @classmethod
    def on_player_death(cls, ev, signal):
        cls.game_started = False

    @classmethod
    def on_idle(self, update, signal):
        t = time()
        clear = []
        for i, (c, func) in enumerate(self.callbacks):
            if c <= t:
                func()
                clear.append(i)
        for i in reversed(clear):
            del self.callbacks[i]
    
    @classmethod
    def on_key_released(cls, ev, signal):
        if ev.key == k.Escape:
            signal(ToggleMenu())


class Particle(ppb.sprites.Sprite):
    image = ppb.Image("resources/sparkle1.png")
    opacity = 128
    opacity_mode = 'add'
    color = COLOR['WHITE']
    size = 2
    rotation = 0

    def __init__(self, *args, **kwargs):
        self.color = kwargs.pop('color', COLOR['WHITE'])
        super().__init__(*args, **kwargs)


class ParticleSystem(System):
    sparkles = []
    index = 0
    size = 100

    @classmethod
    def on_scene_started(cls, ev, signal):
        t = Tweener()
        cls.t = t
        ev.scene.add(t)

        for _ in range(cls.size):
            position = V(random()*12 - 6, random()*12 - 6)
            s = Particle(position=position)
            s.opacity = 0
            s.size = 0
            ev.scene.add(s)
            cls.sparkles.append(s)

    @classmethod
    def spawn(cls, pos, color, heading=None, tsize=2.5):
        s = cls.sparkles[cls.index]
        cls.index = (cls.index + 1) % cls.size
        if color == COLOR_BLACK:
            s.opacity_mode = 'blend'
            s.opacity = 255
        else:
            s.opacity_mode = 'add'
            s.opacity = 128
        s.color = color
        s.position = pos
        s.rotation = randint(0, 260)
        s.size = 1.5
        s.layer = 100
        cls.t.tween(s, 'opacity', 0, 0.5, easing='linear')
        cls.t.tween(s, 'size', tsize, 0.5, easing='linear')
        delay(0.5, lambda: setattr(s, 'size', 0))
        if heading:
            cls.t.tween(s, 'position', heading, 0.5, easing='linear')


class ScoreBoard(System):
    
    @classmethod
    def on_scene_started(cls, ev, signal):
        cls.score = 0
        cls.text = Text(str(cls.score), V(0, 4))
        ev.scene.add(cls.text)
    
    @classmethod
    def on_score_points(cls, ev, signal):
        cls.score += ev.points
        cls.text.text = str(cls.score)
        signal(ScoreUpdated(cls.score))
    
    @classmethod
    def on_score_set(cls, ev, signal):
        cls.score = ev.points
        cls.text.text = str(cls.score)
        signal(ScoreUpdated(cls.score))


@dataclass
class Bar:
    color: Tuple[int]
    position: ppb.Vector
    value: int = 10
    max: int = 10
    size: int = 0
    bg: ppb.Sprite = None
    segments: Tuple[ppb.Sprite] = ()

    BAR_BG = ppb.Image("resources/BAR_BG.png")
    BAR_SEGMENT = ppb.Image("resources/BAR_SEGMENT.png")

    def __hash__(self):
        return hash(id(self))

    def __init__(self, scene, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.bg = ppb.Sprite(
            position=self.position,
            image=self.BAR_BG,
            size=1/4,
            layer=50,
        )
        scene.add(self.bg)

        segments = []
        for i in range(16):
            segment = ppb.Sprite(
                position=self.position + V(i/4 - 2, 0),
                image=self.BAR_SEGMENT,
                color=self.color,
                size=1/4,
                layer=51,
            )
            segments.append(segment)
            scene.add(segment)
        self.segments = tuple(segments)

        self.set_value(10)
    
    def set_max(self, new_max):
        self.max = new_max
        self.set_value(self.value)
    
    def set_value(self, value):
        self.value = value
        if value == 0:
            p = 0
        else:
            p = int(value / self.max * 16)
        for i, segment in enumerate(self.segments):
            if i >= p:
                segment.size = 0
            else:
                segment.size = 1/4


from cloud import CloudSystem
from mushroom import Mushroom
from viking import Viking
from floatingnumbers import FloatingNumberSystem

import ui


class VikingSpawn(System):

    def on_update(self, ev, signal):
        vikings = list(ev.scene.get(tag='viking'))
        if not vikings:
            for i in range(randint(3, 5)):
                ev.scene.add(Viking(
                    layer=10,
                    position=ppb.Vector(5, 0).rotate(randint(0, 360)),
                ), tags=['viking'])


@dataclass
class PlaceNewMushroom:
    pass

class MushroomPlacement(System):

    def on_scene_started(self, ev, signal):
        self.mode = "waiting"
        signal(ui.CreateButton("Mushroom", enabled=False))
    
    def on_score_updated(self, ev, signal):
        if ev.points >= 3:
            signal(ui.EnableButton("Mushroom"))
        else:
            signal(ui.DisableButton("Mushroom"))

    def on_ui_button_pressed(self, ev, signal):
        if ev.label == "Mushroom":
            self.mode = "placing"
    
    def on_button_released(self, ev, signal):
        if self.mode == "placing":
            ev.scene.add(Mushroom(
                position=ev.position,
                layer=10,
            ), tags=['mushroom'])
            self.mode = "waiting"
            signal(ScorePoints(-3))





def setup(scene):
    # text = Text("Hello, World", V(0, -4))
    # scene.add(text)

    scene.add(ppb.Sprite(
        image=ppb.Image("resources/BACKGROUND.png"),
        size=12,
        layer=-1,
    ), tags=['bg'])

    scene.add(Mushroom(
        layer=10,
    ), tags=['mushroom'])

    scene.add(Mushroom(
        position=ppb.Vector(2, 0),
        layer=10,
    ), tags=['mushroom'])


ppb.run(
    setup=setup,
    basic_systems=(CustomRenderer, Updater, EventPoller, SoundController, AssetLoadingSystem),
    systems=[
        TickSystem,
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
