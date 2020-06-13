from dataclasses import dataclass
import math
import random
from time import perf_counter

import ppb
from ppb.systemslib import System
from ppb.events import ButtonPressed, ButtonReleased, Update

import constants as C
from utils.spritedepth import pos_to_layer

import ppb_tween as tweening


@dataclass
class MushroomAttack:
    cloud_id: int
    target: 'viking.Viking'
    dmg: int = 1
    scene: ppb.BaseScene = None


class Cloud(ppb.sprites.Sprite):
    heading: ppb.Vector
    image = ppb.Image("resources/cloud.png")
    speed: float = 5.0
    lifetime: float = 1.0
    size: float = 2.0
    last_hit_time: float = 0.0
    opacity: int = 255

    def __init__(self, *args, **kwargs):
        self.cloud_id = kwargs.get('cloud_id')
        super().__init__(*args, **kwargs)

    def on_update(self, ev, signal):
        self.lifetime -= ev.time_delta * 0.5

        t = 1.0 - self.lifetime
        if self.lifetime <= 0.0:
            ev.scene.remove(self)

    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position)
        assert self.layer > 0, self.layer


class CloudSystem(System):
    STEPS = 12

    def on_emit_cloud(self, ev, signal):
        r = 360 / self.STEPS
        for i in range(self.STEPS):
            w = random.randrange(-r//2, r//2)
            heading = ppb.Vector(C.SMOOSHROOM_CLOUD_RADIUS_MAX, 0).rotate(w + r * i)
            cloud = Cloud(heading=heading, position=ev.position, cloud_id=ev.cloud_id)
            cloud.size = 0.0
            ev.scene.add(cloud)

            tweening.tween(cloud, "position", ev.position + heading, 1.0, easing='quint_out')
            tweening.tween(cloud, "size", 1.0, 1.0, easing='quad_out')
            tweening.tween(cloud, "opacity", 0.0, 1.0, easing='linear')
