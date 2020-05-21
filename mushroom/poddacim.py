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

    # def on_button_pressed(self, ev: ButtonPressed, signal):
    #     clicked = super().on_button_pressed(ev, signal)
    #     if clicked:
    #         pass


    def on_update(self, ev: Update, signal):
        t = perf_counter()
        if self.last_shot + 1.0 <= t:
            self.last_shot = t
            vikings = [v for v in ev.scene.get(tag='viking') if v.hp > 0]
            vikings.sort(key=lambda viking: (viking.position - self.position).length)
            if vikings:
                dist = (vikings[0].position - self.position).length
                if dist < 4.0:
                    pod = PoddacimPod(position=self.position)
                    tweening.tween(pod, 'position', vikings[0].position, 0.25)
                    ev.scene.add(pod)

                    def _():
                        vikings[0].on_mushroom_attack(MushroomAttack(None, vikings[0]), signal)
                        ev.scene.remove(pod)
                    delay(0.25, _)
