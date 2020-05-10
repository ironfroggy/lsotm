from dataclasses import dataclass
import math
import random

import ppb
from ppb.systemslib import System
from ppb.events import ButtonPressed, ButtonReleased, Update

from easing import out_quad
import tweening


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


@dataclass
class MushroomAttack:
    mushroom: 'mushroom.Mushroom'
    target: 'viking.Viking'


class Cloud(ppb.sprites.Sprite):
    heading: ppb.Vector
    image = ppb.Image("resources/cloud.png")
    speed: float = 5.0
    lifetime: float = 1.0
    size: float = 2.0
    
    def on_update(self, ev: Update, signal):
        self.lifetime -= ev.time_delta * 0.5

        t = 1.0 - self.lifetime
        self.opacity = tweening.lerp(255, 0, t)
        self.size = tweening.lerp(0.0, 1.0, t)
        self.speed = tweening.lerp(2.0, 0.0, out_quad(t))
        if self.lifetime <= 0.0:
            ev.scene.remove(self)
        else:
            self.position += self.heading * self.speed * ev.time_delta

            # Collision check this cloud with all the vikings
            for viking in ev.scene.get(tag='viking'):
                d = dist(viking.position, self.position)
                if d < 1.5:
                    signal(MushroomAttack(None, viking))


class CloudSystem(System):
    STEPS = 12

    def on_emit_cloud(self, ev, signal):
        r = 360 / self.STEPS
        for i in range(self.STEPS):
            w = random.randrange(-r/2, r/2)
            heading = ppb.Vector(1, 0).rotate(w + r * i)
            cloud = Cloud(heading=heading, position=ev.position)
            cloud.size = 0
            ev.scene.add(cloud)
