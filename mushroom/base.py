from dataclasses import dataclass
from math import cos, pi

import ppb
from ppb.utils import get_time
from ppb.events import ButtonPressed, ButtonReleased, Update

from controllers.meters import MeterUpdate, MeterRemove
from systems.floatingnumbers import CreateFloatingNumber
from systems.particles import ParticleSpawnerCreate
from systems import ui

from utils.spritedepth import pos_to_layer

from ppb_timing import repeat, delay
from ppb_tween import tween

from events import *
from constants import *


@dataclass
class PlaceNewMushroom:
    pass


class Mushroom(ppb.sprites.Sprite):
    size: float = 2.0
    approach_distance: float = 1.5

    health: int = 10

    growing: float = 0.0
    absorbing: float = 0.0
    absorb_radius: float = 3.0

    # TODO: Can any of these be combined?
    smooshed: bool = False
    smoosh_time: float = 0.0
    pressed_time: float = 0.0
    emit_t: float = 0.0
    toxins: float = 1.0

    # PPB Events
    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position)
        t = get_time()
        if self.absorbing > t or self.growing:
            s = (cos((self.absorbing - t + 1.0) * pi) + 1.0) * 0.5 + 0.5
            o = round(64 * s)
            self.root.opacity = o
        elif self.root.opacity > 0:
            self.root.opacity -= 1

    def on_button_pressed(self, ev: ButtonPressed, signal) -> bool:
        d = (self.position - ev.position).length
        if d < 1.0:
            self.smooshed = True
            self.smoosh_time = 0.0
            self.pressed_time = get_time()
        return d < 1.0
    
    def on_button_released(self, ev: ButtonReleased, signal):
        self.smooshed = False
        # TODO: Animate the bounce back
        self.image = self.smoosh_sprites[0]

    # Gameplay events
    def on_viking_attack(self, ev, signal):
        if ev.target is self:
            self.health = max(0, self.health - ev.dmg)
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))
            signal(MeterUpdate(self, 'health', self.health / 10))
            if self.health <= 0:
                signal(MushroomDeath(self))
                # TODO: Move to event handler for above
                ev.scene.remove(self)
                ev.scene.remove(self.root)
                signal(MeterRemove(self))
    
    def on_viking_death(self, ev, signal):
        v = ev.viking.position
        d = (self.position - v).length
        if d < self.absorb_radius and not ev.claimed:
            self.absorbing = get_time() + 5.0
            signal(ParticleSpawnerCreate(
                source=(v + ppb.Vector(-1, -0.4), v),
                dest=(v + ppb.Vector(-0.9, 1.25), v + ppb.Vector(-0.1, 1)),
                color=COLOR['YELLOW'],
                lifespan=5.0,
            ))
            delay(5.0, lambda: signal(ScorePoints(1)))
            delay(5.0, lambda: signal(CreateFloatingNumber(1, ev.viking.position + ppb.Vector(0, 1), COLOR['YELLOW'])))
            ev.claimed = True
