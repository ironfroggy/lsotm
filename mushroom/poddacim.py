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
from cloud import MushroomAttack
from .base import Mushroom
from systems.timer import delay



MUSHROOM_SPRITES = [
    ppb.Image("resources/mushroom/poddacim_0.png"),
    ppb.Image("resources/mushroom/poddacim_1.png"),
    ppb.Image("resources/mushroom/poddacim_2.png"),
    ppb.Image("resources/mushroom/poddacim_3.png"),
]


class PoddacimPod(ppb.Sprite):
    image = ppb.Image("resources/mushroom/pod.png")


class Poddacim(Mushroom):
    smoosh_sprites = MUSHROOM_SPRITES
    image: ppb.Image = smoosh_sprites[0]
    
    last_shot: float = 0.0
    smooshed: bool = False
    exhausted: bool = False

    def on_button_pressed(self, ev: ButtonPressed, signal):
        clicked = super().on_button_pressed(ev, signal)
        if clicked:
            self.smooshed = True
    
    def on_button_released(self, ev: ButtonPressed, signal):
        self.smooshed = False

    def on_update(self, ev: Update, signal):
        t = perf_counter()
        r = 0.25 if self.smooshed else 1.0

        if not self.exhausted and self.last_shot + r <= t and self.toxins > C.PODDACIM_POD_RATE:
            self.last_shot = t
            vikings = [v for v in ev.scene.get(tag='viking') if v.hp > 0]
            vikings.sort(key=lambda viking: (viking.position - self.position).length)
            if vikings:
                dist = (vikings[0].position - self.position).length
                if dist < C.PODDACIM_ATK_RADIUS:
                    pod = PoddacimPod(position=self.position)
                    tweening.tween(pod, 'position', vikings[0].position, 0.25)
                    ev.scene.add(pod)
                    self.toxins = max(0.0, round(self.toxins - C.PODDACIM_POD_RATE, 2))
                    signal(MeterUpdate(self, 'toxins', self.toxins))

                    # When toxins hit 0, Poddacim becomes exhausted
                    if self.toxins == 0.0:
                        self.exhausted = True

                    def _():
                        vikings[0].on_mushroom_attack(MushroomAttack(None, vikings[0], C.PODDACIM_POD_DMG), signal)
                        ev.scene.remove(pod)
                    delay(0.25, _)

        # If the mushroom isn't being smooshed, increase toxin accumulator
        # and reset the cloud accumulator.
        if not self.smooshed or self.exhausted:
            self.toxins = min(1.0, self.toxins + ev.time_delta * C.PODDACIM_TOXIN_CHARGE)
            signal(MeterUpdate(self, 'toxins', self.toxins))

            # When toxins are full, no longer exhausted
            if self.toxins == 1.0:
                self.exhausted = False
