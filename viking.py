from dataclasses import dataclass
import math
from random import choice
import time

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update

from easing import out_quad
from events import ScorePoints
from statemachine import StateMachine
import tweening


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


VIKING_BASE = [
    ppb.Image(f"resources/viking/l0_sprite_1.png")
    # for i in range(1, 8)
]

VIKING_HAT = [
    ppb.Image(f"resources/viking/hat_{i:02d}.png")
    for i in range(1, 11)
]

VIKING_CLOTHES = [
    ppb.Image(f"resources/viking/clothes_{i:02d}.png")
    for i in range(1, 16)
]


@dataclass
class VikingAttack:
    target: 'mushroom.Mushroom'
    dmg: int


class State:
    def enter_state(self):
        pass


class ApproachState(State):

    @staticmethod
    def on_update(self, ev, signal):
        t = time.monotonic()
        if not self.target or not self.target.health:
            self.target = choice(list(ev.scene.get(tag='mushroom')))
        d = dist(self.position, self.target.position)
        if d > 1.0:
            h = (self.target.position - self.position).normalize()
            self.position += h * self.speed * ev.time_delta
        else:
            self.set_state("cooldown")
    
class AttackState(State):
    @staticmethod
    def on_update(self, ev, signal):
        if self.target.health == 0:
            self.target = None
            self.set_state('cooldown')
        else:
            d = dist(self.position, self.target.position)
            if d <= 1.0:
                signal(VikingAttack(self.target, 1))
                self.set_state("cooldown")
            else:
                self.set_state("approach")

class DieingState(State):
    @staticmethod
    def enter_state(self):
        self.sprite_base.opacity = 128

    @staticmethod
    def on_update(self, ev, signal):
        ev.scene.remove(self)
        ev.scene.remove(self.sprite_base)
        ev.scene.remove(self.sprite_clothes)
        ev.scene.remove(self.sprite_hat)
        signal(ScorePoints(1))

class CooldownState(State):
    def on_update(self, ev, signal):
        if self.state_time() > 0.5:
            if not self.target or not self.target.health:
                self.target = choice(list(ev.scene.get(tag='mushroom')))
            d = dist(self.position, self.target.position)
            if d <= 1.0:
                self.set_state("attack")
            else:
                self.set_state("approach")

STATES = {
    'attack': AttackState,
    'approach': ApproachState,
    'dead': DieingState,
    'cooldown': CooldownState,
}


class Viking(ppb.Sprite):
    size: float = 0.0
    speed: float = 0.5
    hp: int = 3
    last_hit: float = 0.0
    target: ppb.Sprite = None

    sprite_base: ppb.Sprite = None
    sprite_hat: ppb.Sprite = None
    sprite_clothes: ppb.Sprite = None

    state = ApproachState()
    last_state_change: float = 0.0

    def set_state(self, state):
        self.state = STATES[state]
        self.state.enter_state(self)
        self.last_state_change = time.monotonic()

    def state_time(self):
        return time.monotonic() - self.last_state_change

    def on_pre_render(self, ev, signal):
        if self.sprite_base is None:
            self.sprite_base = ppb.Sprite(image=choice(VIKING_BASE), layer=self.layer, size=2)
            self.sprite_clothes = ppb.Sprite(image=choice(VIKING_CLOTHES), layer=self.layer + 1, size=2)
            self.sprite_hat = ppb.Sprite(image=choice(VIKING_HAT), layer=self.layer + 1, size=2)

            ev.scene.add(self.sprite_base)
            ev.scene.add(self.sprite_clothes)
            ev.scene.add(self.sprite_hat)
        self.sprite_base.position = self.position
        self.sprite_hat.position = self.position
        self.sprite_clothes.position = self.position
    
    def on_update(self, ev: Update, signal):
        self.state.on_update(self, ev, signal)
    
    def on_cloud_poison(self, ev, signal):
        d = dist(self.position, ev.position)
        if d < 0.5:
            self.size = max(0.0, self.size - 0.1)
    
    def hit(self, scene):
        t = time.monotonic()
        if t - self.last_hit >= 1.0:
            self.set_state('cooldown')
            self.last_hit = t
            self.hp -= 1
            if self.hp <= 0:
                self.set_state('dead')
