from dataclasses import dataclass
import math
from time import perf_counter

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update
from ppb.systemslib import System

import ppb_tween as tweening

import constants as C
from events import ScorePoints
from controllers.meters import MeterUpdate, MeterRemove
from ppb_timing import delay
from systems.cloud import MushroomAttack
from .base import Mushroom



MUSHROOM_SPRITES = [
    ppb.Image("resources/mushroom/mushroom_0.png"),
    ppb.Image("resources/mushroom/mushroom_1.png"),
    ppb.Image("resources/mushroom/mushroom_2.png"),
    ppb.Image("resources/mushroom/mushroom_3.png"),
]


@dataclass
class EmitCloud:
    position: ppb.Vector
    cloud_id: int


def debounce(obj, marker, delay):
    v = getattr(obj, marker, 0.0)
    t = perf_counter()
    if v + delay < t:
        setattr(obj, marker, t)
        return True
    else:
        return False


class Smooshroom(Mushroom):
    smoosh_sprites = MUSHROOM_SPRITES
    image: ppb.Image = smoosh_sprites[0]

    cloud: float = 0.0
    cloud_id: int = 0
    cloud_radius: float = 0.0

    PLACEMENT_RADIUS = C.SMOOSHROOM_CLOUD_RADIUS_MAX

    def on_button_pressed(self, ev: ButtonPressed, signal):
        clicked = super().on_button_pressed(ev, signal)
        if clicked:
            # TODO: This is pretty cludging and won't always match the visual clouds
            self.cloud_radius = 0.5
            self.cloud_id = int(perf_counter() * 1000)
            tweening.tween(self, "cloud_radius", C.SMOOSHROOM_CLOUD_RADIUS_MAX, C.SMOOSHROOM_CLOUD_RADIUS_TIME, easing='quad_out')

    def on_update(self, ev: Update, signal):
        # If the mushroom is being smooshed and it has toxins to squish...
        if self.toxins and self.smooshed:

            # Set smoosh frame
            t = tweening.EASING['quad_out'](self.smoosh_time)
            assert 0.0 <= t <= 1.0
            i = tweening.lerp(0, 3, t)
            self.image = MUSHROOM_SPRITES[i]

            # Accumulate cloud counter from toxin counter
            self.smoosh_time = min(1.0, self.smoosh_time + ev.time_delta)
            self.toxins = max(0.0, self.toxins - ev.time_delta)
            signal(MeterUpdate(self, 'toxins', self.toxins))
            self.cloud = self.cloud + ev.time_delta

            # If the cloud accumulator reaches threashold,
            # emit clouds and clear the accumulator.
            if self.cloud >= C.SMOOSHROOM_TOXIN_DMG_RATE:
                signal(EmitCloud(self.position, self.cloud_id))
                self.pressed_time = perf_counter()
                self.cloud -= C.SMOOSHROOM_TOXIN_DMG_RATE

                for viking in ev.scene.get(tag='viking'):
                    d = (viking.position - self.position).length
                    if d <= self.cloud_radius + 0.5:
                        viking.on_mushroom_attack(MushroomAttack(perf_counter(), viking, scene=ev.scene), signal)

        # If the mushroom isn't being smooshed, increase toxin accumulator
        # and reset the cloud accumulator.
        elif not self.smooshed and self.toxins < 1.0:
            self.toxins = min(1.0, self.toxins + ev.time_delta * C.SMOOSHROOM_TOXIN_CHARGE)
            self.cloud = 0.0
            signal(MeterUpdate(self, 'toxins', self.toxins))

    def on_viking_attack(self, ev, signal):
        super().on_viking_attack(ev, signal)
        if ev.target is self:
            self.smooshed = True

            self.cloud += C.SMOOSHROOM_TOXIN_DMG_RATE
            self.toxins -= C.SMOOSHROOM_TOXIN_DMG_RATE
            self.cloud_radius = 0.5
            self.cloud_id = int(perf_counter() * 1000)
            tweening.tween(self, "cloud_radius", C.SMOOSHROOM_CLOUD_RADIUS_MAX, C.SMOOSHROOM_CLOUD_RADIUS_TIME, easing='quad_out')

            delay(0.25, lambda: setattr(self, 'smooshed', False))
