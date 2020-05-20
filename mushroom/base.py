from dataclasses import dataclass
from time import perf_counter

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update

from controllers.meters import MeterUpdate, MeterRemove
from systems.floatingnumbers import CreateFloatingNumber
from systems import ui

from utils.spritedepth import pos_to_layer


@dataclass
class PlaceNewMushroom:
    pass


class Mushroom(ppb.sprites.Sprite):
    size: float = 2.0

    health: int = 10

    # TODO: Can any of these be combined?
    smooshed: bool = False
    smoosh_time: float = 0.0
    pressed_time: float = 0.0
    emit_t: float = 0.0
    toxins: float = 1.0

    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position)

    def on_button_pressed(self, ev: ButtonPressed, signal) -> bool:
        d = (self.position - ev.position).length
        if d < 1.0:
            self.smooshed = True
            self.smoosh_time = 0.0
            self.pressed_time = perf_counter()

        return d < 1.0
    
    def on_button_released(self, ev: ButtonReleased, signal):
        self.smooshed = False
        # TODO: Animate the bounce back
        self.image = self.smoosh_sprites[0]

    def on_viking_attack(self, ev, signal):
        if ev.target is self:
            self.health = max(0, self.health - ev.dmg)
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))
            signal(MeterUpdate(self, 'health', self.health / 10))
            if self.health <= 0:
                ev.scene.remove(self)
                signal(MeterRemove(self))
