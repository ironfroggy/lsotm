from dataclasses import dataclass
import math
from random import choice, randint, random
import time
import typing

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update
from ppb.features.animation import Animation
from ppb.utils import get_time

import ppb_tween as tweening

from constants import COLOR
from events import ScorePoints
from systems.floatingnumbers import CreateFloatingNumber
from utils.statemachine import StateMachine
from utils.spritedepth import pos_to_layer

from systems.particles import ParticleSystem
from systems.timer import repeat, cancel

# from vikings.corpse import CorpseCtrl


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


@dataclass
class VikingDeath:
    viking: 'Viking'


# TODO: Make this not suck...?
class State:
    
    @staticmethod
    def enter_state(self, scene, signal):
        pass

    @staticmethod
    def on_mushroom_attack(self, ev, signal):
        t = time.monotonic()
        if (ev.cloud_id is None or self.last_hit_by < ev.cloud_id) and self is ev.target:
            if ev.cloud_id is not None:
                self.set_state('cooldown', ev.scene, signal)
                self.last_hit = t
                self.last_hit_by = ev.cloud_id
            self.hp -= 1
            if self.hp <= 0:
                self.set_state('dieing', ev.scene, signal)
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))


class ApproachState(State):

    @staticmethod
    def enter_state(self, scene, signal):
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
            self.set_state("cooldown", ev.scene, signal)
    
class AttackState(State):

    @staticmethod
    def enter_state(self, scene, signal):
        self.sprite_base.image = VIKING_BASE[0]

    @staticmethod
    def on_update(self, ev, signal):
        if self.target.health == 0:
            self.target = None
            self.set_state('cooldown', ev.scene, signal)
        else:
            d = dist(self.position, self.target.position)
            if d <= 1.5:
                signal(VikingAttack(self.target, self.atk))
                self.sprite_base.image = Animation("resources/viking/attack_{0..4}.png", 10)
                self.set_state("cooldown", ev.scene, signal)
            else:
                self.set_state("approach", ev.scene, signal)


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
                    self.set_state("cooldown", ev.scene, signal)
            
            if self.target:
                d = dist(self.position, self.target.position)
                if d <= 1.5:
                    self.set_state("attack", ev.scene, signal)
                else:
                    self.set_state("approach", ev.scene, signal)


class DieingState(State):

    @staticmethod
    def enter_state(self, scene, signal):
        self.sprite_base.image = ppb.Image("resources/viking/dead_bg.png")
        for s in self.sprites:
            tweening.tween(s, 'rotation', 90, 0.5)
            tweening.tween(s, 'opacity', 0, 5.0)
        tweening.tween(self, 'position', s.position + ppb.Vector(-0.5, -0.25), 0.5)
        self.sprite_fg.opacity = 255

        # for mushroom in scene.get(tag='mushroom'):
        #     d = (mushroom.position - self.position).length
        #     if d < 3:
        #         self.nearest_mushroom = mushroom
        #         self.particle_timer = repeat(0.025, lambda: DieingState.spore_particle(self))
        #         mushroom.absorbing = get_time() + 5.0
        #         break
        signal(VikingDeath(self))
    
    # @staticmethod
    # def spore_particle(self):
    #     origin = self.position + ppb.Vector(-0.5 + random(), 0)
    #     heading = self.position + ppb.Vector(-0.5 + random(), 1.0 + random())
    #     ParticleSystem.spawn(origin, COLOR['YELLOW'], heading,
    #         opacity=255, opacity_mode=ppb.flags.BlendModeBlend,
    #     )

    @staticmethod
    def on_update(self, ev, signal):
        if self.state_time() >= 5.0:
            ev.scene.remove(self)
            ev.scene.remove(self.sprite_base)
            ev.scene.remove(self.sprite_clothes)
            ev.scene.remove(self.sprite_hat)

            if self.nearest_mushroom:
                signal(ScorePoints(1))
                signal(CreateFloatingNumber(1, self.position + ppb.Vector(0, 1), COLOR['YELLOW']))
        
        if self.state_time() >= 4.5 and self.particle_timer:
            cancel(self.particle_timer)
    
    @staticmethod
    def on_mushroom_attack(self, ev, signal):
        pass


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
    speed: float = 1.0
    hp: int = 1
    atk: int = 1
    strength: int = 1
    last_hit: float = 0.0
    last_hit_by: int = 0
    target: ppb.Sprite = None
    nearest_mushroom: 'mushrooms.Mushroom' = None

    sprite_base: ppb.Sprite = None
    sprite_hat: ppb.Sprite = None
    sprite_clothes: ppb.Sprite = None

    state: typing.Type[State] = None
    last_state_change: float = 0.0
    particle_timer: 'systems.timer.Timer' = None

    def __init__(self, *args, **kwargs):
        self.strength = kwargs.pop('strength')
        self.hp = max(1, self.strength // 2)
        self.atk = max(1, self.strength - self.hp)
        super().__init__(*args, **kwargs)
        self.state = ApproachState
    
    @property
    def sprites(self):
        yield self.sprite_base
        yield self.sprite_clothes
        yield self.sprite_hat
        yield self.sprite_fg

    def set_state(self, state, scene, signal):
        if self.state != STATES[state]:
            self.last_state_change = time.monotonic()
            self.state = STATES[state]
            self.state.enter_state(self, scene, signal)

    def state_time(self):
        return time.monotonic() - self.last_state_change

    def on_pre_render(self, ev, signal):
        layer = pos_to_layer(self.position)

        if self.sprite_base is None:
            self.sprite_base = ppb.Sprite(
                image=VIKING_WALK,
                layer=layer,
                size=2,
                opacity=255,
            )

            clothes_i = min(len(VIKING_CLOTHES), max(1, self.strength // 2)) - 1
            hat_i = min(len(VIKING_HAT), max(1, self.strength - clothes_i)) - 1
            self.sprite_clothes = ppb.Sprite(image=VIKING_CLOTHES[clothes_i], layer=layer + 0.1, size=2, opacity=255)
            self.sprite_hat = ppb.Sprite(image=VIKING_HAT[hat_i], layer=layer + 0.1, size=2, opacity=255)
            self.sprite_fg = ppb.Sprite(image=ppb.Image("resources/viking/dead_fg.png"), size=2)
            self.sprite_fg.opacity = 0

            ev.scene.add(self.sprite_base)
            ev.scene.add(self.sprite_clothes)
            ev.scene.add(self.sprite_hat)
            ev.scene.add(self.sprite_fg)

        self.sprite_base.position = self.position
        self.sprite_base.layer = layer
        self.sprite_hat.position = self.position
        self.sprite_hat.layer = layer + 0.1
        self.sprite_clothes.position = self.position
        self.sprite_clothes.layer = layer + 0.1
        self.sprite_fg.position = self.position
        self.sprite_fg.layer = layer + 0.2
    
    def on_update(self, ev: Update, signal):
        self.state.on_update(self, ev, signal)
    
    def on_cloud_poison(self, ev, signal):
        d = dist(self.position, ev.position)
        if d < 0.5:
            self.size = max(0.0, self.size - 0.1)
    
    def on_mushroom_attack(self, ev, signal):
        self.state.on_mushroom_attack(self, ev, signal)


class VikingSpawnCtrl:
    active: bool = False
    wave_number: int = 1

    @classmethod
    def create(cls, scene):
        ctrl = cls()
        scene.add(ctrl)
        return ctrl
    
    def start(self):
        self.active = True

    def on_update(self, ev, signal):
        if self.active:
            vikings = list(ev.scene.get(tag='viking'))
            if not vikings:
                danger = self.wave_number
                if danger % 10 == 0:
                    strengths = [danger]
                else:
                    strengths = []
                    while danger:
                        strength = randint(1, danger)
                        strengths.append(strength)
                        danger -= strength
                    
                for i, strength in enumerate(strengths):
                    ev.scene.add(Viking(
                        layer=10,
                        position=ppb.Vector(-10 + i, 0),
                        strength=strength,
                    ), tags=['viking'])
            
                self.wave_number += 1
