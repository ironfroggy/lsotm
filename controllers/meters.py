from dataclasses import dataclass

from sdl2 import (
    SDL_FLIP_NONE,
)

import ppb
from ppb import flags

from constants import *
from ppb_timing import delay
from utils.imagesequence import Sequence

from ppb_tween import Tweener


@dataclass
class MeterUpdate:
    target: object
    attr: str
    value: float
    flash: bool = False


@dataclass
class MeterRemove:
    target: object
    attr: str = None


class CtrlMeter:
    position: ppb.Vector
    size = 2.0 # Not visible

    def __init__(self, image_seq, target, attr, track, color=COLOR['WHITE'], flip=SDL_FLIP_NONE):
        self.meter_sprite = ppb.Sprite(
            image=image_seq.copy(),
            position=track.position,
            size=self.size,
            layer=LAYER_METER,
            tint=color,
            flip=flip,
            opacity=0,
        )
        self.target = target
        self.attr = attr
        self.track = track
        self.tweener = Tweener()
        self.timer = None
        self.original_color = color

    def __image__(self):
        return None

    @classmethod
    def create(cls, scene, *args, **kwargs):
        new = cls(*args, **kwargs)
        new.add_to_scene(scene)

    def add_to_scene(self, scene):
        scene.add(self)
        scene.add(self.meter_sprite)
        scene.add(self.tweener)

    def on_pre_render(self, ev, signal):
        self.meter_sprite.position = self.track.position

    def on_meter_update(self, ev: MeterUpdate, signal):
        if self.target == ev.target and self.attr == ev.attr:
            if ev.flash:
                self.meter_sprite.tint = (128, 128, 128)
            else:
                self.meter_sprite.tint = self.original_color
            self.meter_sprite.image.set_ratio(ev.value)
            self.meter_sprite.opacity = 255
            self.tweener.cancel()
            if self.timer:
                self.timer.cancel()
            self.timer = delay(3, lambda:
                self.tweener.tween(self.meter_sprite, 'opacity', 0, 1)
            )

    def on_meter_remove(self, ev: MeterRemove, signal):
        if self.target == ev.target and (self.attr == ev.attr or ev.attr is None):
            ev.scene.remove(self.meter_sprite)
            ev.scene.remove(self.tweener)
            ev.scene.remove(self)
