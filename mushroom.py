import math

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update

from easing import out_quad


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


class Mushroom(ppb.sprites.Sprite):
    image = ppb.Image("resources/smooshroom.png")

    smooshed: bool = False
    smoosh_time: float = 0.0
    
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
            t = out_quad(self.smoosh_time) * 0.2
            self.size = 1.0 - t
        else:
            self.size = 1.0
