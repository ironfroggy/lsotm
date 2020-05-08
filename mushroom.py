from dataclasses import dataclass
import math

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update

from easing import out_quad
from events import ScorePoints


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


@dataclass
class EmitCloud:
    position: ppb.Vector


class Mushroom(ppb.sprites.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 1.0

    health: int = 10

    smooshed: bool = False
    smoosh_time: float = 0.0

    emit_t: float = 0.0
    
    def on_button_pressed(self, ev: ButtonPressed, signal):
        d = dist(self.position, ev.position)
        if d < 1.0:
            self.smooshed = True
            self.smoosh_time = 0.0
    
    def on_button_released(self, ev: ButtonReleased, signal):
        self.smooshed = False

    def on_update(self, ev: Update, signal):
        if self.smooshed:
            self.smoosh_time = min(1.0, self.smoosh_time + ev.time_delta)
            if self.smoosh_time < 0.5:
                if self.emit_t <= 0.0:
                    self.emit_t = 0.1
                    signal(EmitCloud(self.position))
                else:
                    self.emit_t -= ev.time_delta
            t = out_quad(self.smoosh_time) * 0.2
            self.size = 2.0 * (1.0 - t)
        else:
            self.size = 2.0
    
    def on_viking_attack(self, ev, signal):
        if ev.target is self:
            self.health = max(0, self.health - ev.dmg)
            print('mushroom is', self.health)
            if self.health <= 0:
                print('mushroom is dead')
                ev.scene.remove(self)
