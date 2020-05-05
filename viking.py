import math
import time

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update

from easing import out_quad


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


class Viking(ppb.sprites.Sprite):
    image = ppb.Image("resources/viking.png")
    speed: float = 0.5
    hp: int = 3
    last_hit: float = 0.0
    
    def on_update(self, ev: Update, signal):
        t = time.monotonic()

        if t - self.last_hit >= 0.5:
            start = self.position
            speed = self.speed
            end = ppb.Vector(0, 0)
            elapsed = ev.time_delta

            h = (end - start).normalize()

            self.position += h * speed * elapsed
    
    def on_cloud_poison(self, ev, signal):
        d = dist(self.position, ev.position)
        if d < 0.5:
            self.size = max(0.0, self.size - 0.1)
    
    def hit(self, scene):
        t = time.monotonic()
        if t - self.last_hit >= 1.0:
            self.last_hit = t
            self.hp -= 1
            if self.hp <= 0:
                scene.remove(self)
