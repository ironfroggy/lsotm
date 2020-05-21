from dataclasses import dataclass
import math
from random import choice, randint
import time
import typing

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update
from ppb.features.animation import Animation

import ppb_tween as tweening

from constants import COLOR
from events import ScorePoints
from systems.floatingnumbers import CreateFloatingNumber
from utils.statemachine import StateMachine
from utils.spritedepth import pos_to_layer


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


VIKING_ATK = Animation("resources/viking/l0_sprite_{1..7}.png", 10)
VIKING_WALK = Animation("resources/viking/l0_sprite_{1..7}.png", 10)

VIKING_BASE = [
    ppb.Image("resources/viking/l0_sprite_1.png")
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


# TODO: Replace with direct method and command attacker/attackee interface
@dataclass
class VikingAttack:
    target: 'mushroom.Mushroom'
    dmg: int


# TODO: Make this not suck...?
class State:
    
    @staticmethod
    def enter_state(self):
        pass

    @staticmethod
    def on_mushroom_attack(self, ev, signal):
        t = time.monotonic()
        if (ev.cloud_id is None or self.last_hit_by < ev.cloud_id) and self is ev.target:
            if ev.cloud_id is not None:
                self.set_state('cooldown')
                self.last_hit = t
                self.last_hit_by = ev.cloud_id
            self.hp -= 1
            if self.hp <= 0:
                self.set_state('dieing')
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))


class ApproachState(State):

    @staticmethod
    def enter_state(self):
        self.sprite_base.image = VIKING_WALK

    @staticmethod
    def on_update(self, ev, signal):
        t = time.monotonic()
        if not self.target or not self.target.health:
            mushrooms = list(ev.scene.get(tag='mushroom'))
            if mushrooms:
                self.target = choice(mushrooms)
        d = dist(self.position, self.target.position)
        if d >= 1.5:
            h = (self.target.position - self.position).normalize()
            self.position += h * self.speed * ev.time_delta
        else:
            self.set_state("cooldown")
    
class AttackState(State):

    @staticmethod
    def enter_state(self):
        self.sprite_base.image = VIKING_BASE[0]

    @staticmethod
    def on_update(self, ev, signal):
        if self.target.health == 0:
            self.target = None
            self.set_state('cooldown')
        else:
            d = dist(self.position, self.target.position)
            if d <= 1.5:
                signal(VikingAttack(self.target, 1))
                self.sprite_base.image = Animation("resources/viking/attack_{0..4}.png", 10)
                self.set_state("cooldown")
            else:
                self.set_state("approach")


class DieingState(State):

    @staticmethod
    def enter_state(self):
        self.sprite_base.image = VIKING_BASE[0]

    @staticmethod
    def on_update(self, ev, signal):
        o = tweening.lerp(255, 0, self.state_time())

        self.sprite_base.opacity = o
        self.sprite_clothes.opacity = o
        self.sprite_hat.opacity = o

        if self.state_time() >= 1.0:
            ev.scene.remove(self)
            ev.scene.remove(self.sprite_base)
            ev.scene.remove(self.sprite_clothes)
            ev.scene.remove(self.sprite_hat)
            signal(ScorePoints(1))
            signal(CreateFloatingNumber(1, self.position, COLOR['YELLOW']))
    
    @staticmethod
    def on_mushroom_attack(self, ev, signal):
        pass


class CooldownState(State):

    @staticmethod
    def on_update(self, ev, signal):
        if self.state_time() >= 0.5:
            self.sprite_base.image = VIKING_BASE[0]
        if self.state_time() >= 1.0:
            if not self.target or not self.target.health:
                try:
                    self.target = choice(list(ev.scene.get(tag='mushroom')))
                except IndexError:
                    self.target = None
                    self.set_state("cooldown")
            
            if self.target:
                d = dist(self.position, self.target.position)
                if d <= 1.5:
                    self.set_state("attack")
                else:
                    self.set_state("approach")

STATES = {
    'attack': AttackState,
    'approach': ApproachState,
    'dieing': DieingState,
    'cooldown': CooldownState,
}


def state_method(name):
    def _(self, ev, signal):
        handler = getattr(self.state, name, None)
        if handler:
            handler(self, ev, signal)
    return _


class Viking(ppb.Sprite):
    size: float = 0.0
    speed: float = 0.5
    hp: int = 3
    last_hit: float = 0.0
    last_hit_by: int = 0
    target: ppb.Sprite = None

    sprite_base: ppb.Sprite = None
    sprite_hat: ppb.Sprite = None
    sprite_clothes: ppb.Sprite = None

    state: typing.Type[State] = None
    last_state_change: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = ApproachState

    def set_state(self, state):
        if self.state != STATES[state]:
            self.last_state_change = time.monotonic()
            self.state = STATES[state]
            self.state.enter_state(self)

    def state_time(self):
        return time.monotonic() - self.last_state_change

    def on_pre_render(self, ev, signal):
        layer = pos_to_layer(self.position)
        if self.sprite_base is None:
            self.sprite_base = ppb.Sprite(
                image=VIKING_WALK,
                layer=layer,
                size=2,
            )
            self.sprite_clothes = ppb.Sprite(image=choice(VIKING_CLOTHES), layer=layer + 0.1, size=2)
            self.sprite_hat = ppb.Sprite(image=choice(VIKING_HAT), layer=layer + 0.1, size=2)

            ev.scene.add(self.sprite_base)
            ev.scene.add(self.sprite_clothes)
            ev.scene.add(self.sprite_hat)
        self.sprite_base.position = self.position
        self.sprite_base.layer = layer
        self.sprite_hat.position = self.position
        self.sprite_hat.layer = layer + 0.1
        self.sprite_clothes.position = self.position
        self.sprite_clothes.layer = layer + 0.1
    
    def on_update(self, ev: Update, signal):
        self.state.on_update(self, ev, signal)
    
    def on_cloud_poison(self, ev, signal):
        d = dist(self.position, ev.position)
        if d < 0.5:
            self.size = max(0.0, self.size - 0.1)
    
    def on_mushroom_attack(self, ev, signal):
        self.state.on_mushroom_attack(self, ev, signal)


class VikingSpawn(ppb.systemslib.System):

    def on_update(self, ev, signal):
        vikings = list(ev.scene.get(tag='viking'))
        if not vikings:
            for i in range(randint(1, 5)):
                ev.scene.add(Viking(
                    layer=10,
                    position=ppb.Vector(0, randint(5, 10)).rotate(randint(0, 360)),
                ), tags=['viking'])
