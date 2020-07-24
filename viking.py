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

from constants import *
from events import ScorePoints
from systems.floatingnumbers import CreateFloatingNumber
from utils.statemachine import StateMachine
from utils.spritedepth import pos_to_layer

from systems.particles import ParticleSystem
from systems.entities import SpriteAdded, SpriteRemoved, RemoveSprite, create_sprite
from ppb_timing import repeat

# from vikings.corpse import CorpseCtrl


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


IMAGE_SHIELD = ppb.Image("resources/viking/shield.png")

VIKING_ATK = Animation("resources/viking/l0_sprite_{1..7}.png", 10)
VIKING_WALK = Animation("resources/viking/l0_sprite_{1..7}.png", 10)

VIKING_BASE = [
    ppb.Image("resources/viking/l0_sprite_1.png")
    # for i in range(1, 8)
]

VIKING_HAIR = [
    None,
    ppb.Image(f"resources/viking/maiden_hair_0.png"),
    ppb.Image(f"resources/viking/maiden_hair_1.png"),
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
    claimed: bool = False


@dataclass
class VikingSpawningDone:
    pass


# TODO: Make this not suck...?
class State:
    
    @staticmethod
    def enter_state(self, scene, signal):
        pass
    
    @staticmethod
    def on_update(self, ev, signal):
        pass
    
    @staticmethod
    def on_pre_render(self, ev, signal):
        pass

    @staticmethod
    def on_mushroom_attack(self, ev, signal):
        t = time.monotonic()
        if (ev.cloud_id is None or self.last_hit_by < ev.cloud_id) and self is ev.target:
            if ev.cloud_id is not None:
                self.set_state('cooldown', ev.scene, signal)
                self.last_hit = t
                self.last_hit_by = ev.cloud_id
            if self.shield:
                self.shield -= 1
                signal(CreateFloatingNumber(-1, self.position, (0, 0, 255)))
                if self.shield == 0:
                    self.parts['shield'].opacity = 0
            else:
                self.hp -= 1
                if self.hp <= 0:
                    self.set_state('dieing', ev.scene, signal)
                signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))


class ApproachState(State):

    @staticmethod
    def enter_state(self, scene, signal):
        self.parts['base'].image = VIKING_WALK
        self.find_next_target(scene)
    
    @staticmethod
    def on_pre_render(self, ev, signal):
        if not self.target or not self.target.health:
            self.set_state("cooldown", ev.scene, signal)
        elif not self.next_pos:
            self.set_state("cooldown", ev.scene, signal)
        else:
            # Distances from the viking to the next point in the path and to
            # the final target
            ds = dist(self.position, self.next_pos)
            dt = dist(self.position, self.target.position)

            # If we've reached the next point in the path but we still aren't at
            # the final target, move along in the path points.
            if ds < 0.05 and self.target_path_step < len(self.target_path) - 1:
                self.target_path_step += 1

            # If we're still further from the target, keep walking
            if self.next_pos is None:
                self.set_state("cooldown", ev.scene, signal)
            else:
                h = (self.next_pos - self.position).normalize()
                self.position += h * self.speed * ev.time_delta
                
    
class AttackState(State):

    @staticmethod
    def enter_state(self, scene, signal):
        self.parts['base'].image = VIKING_BASE[0]
        self.attack_cooldown = 1.0

    @staticmethod
    def on_update(self, ev, signal):
        if self.target.health == 0:
            self.target = None
            self.set_state('cooldown', ev.scene, signal)
            return

        if self.attack_cooldown > 0.0:
            self.attack_cooldown -= ev.time_delta
        else:
            d = dist(self.position, self.next_pos)
            if d <= 1.5:
                signal(VikingAttack(self.target, self.atk))
                self.attack_cooldown = 1.0
                self.parts['base'].image = Animation("resources/viking/attack_{0..4}.png", 10)
            else:
                self.set_state("approach", ev.scene, signal)


class CooldownState(State):

    @staticmethod
    def on_update(self, ev, signal):
        self.parts['base'].image = VIKING_BASE[0]
        if not self.target or not self.target.health:
            try:
                self.find_next_target(ev.scene)
            except IndexError:
                self.target = None
                self.set_state("cooldown", ev.scene, signal)
        
        if self.target:
            d = dist(self.position, self.target.position)

            if d <= self.target.approach_distance:
                self.set_state("attack", ev.scene, signal)
            else:
                self.set_state("approach", ev.scene, signal)


class DieingState(State):

    @staticmethod
    def enter_state(self, scene, signal):
        self.parts['base'].image = ppb.Image("resources/viking/dead_bg.png")
        for s in self.sprites:
            tweening.tween(s, 'rotation', 90, 0.5)
            tweening.tween(s, 'opacity', 0, 5.0)
        tweening.tween(self, 'position', self.position + ppb.Vector(-0.5, -0.25), 0.5)
        self.parts['corpse'].opacity = 255
        signal(VikingDeath(self))

    @staticmethod
    def on_update(self, ev, signal):
        if self.state_time() >= 5.0:
            signal(RemoveSprite(self))
            if self.particle_timer:
                ev.scene.remove(self.particle_timer)
        
        if self.state_time() >= 4.5 and self.particle_timer:
            self.particle_timer.cancel()
    
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
    speed: float = 1.5
    hp: int = 1
    atk: int = 1
    strength: int = 1
    last_hit: float = 0.0
    last_hit_by: int = 0
    shield: bool = False

    target_path_step: int = 0
    target_path: typing.List[typing.Tuple[float, float]] = None
    target: ppb.Sprite = None
    # nearest_mushroom: 'mushrooms.Mushroom' = None

    parts: [ppb.Sprite] = None

    state: typing.Type[State] = None
    last_state_change: float = 0.0
    particle_timer: 'systems.timer.Timer' = None

    def __init__(self, *args, **kwargs):
        for k, v in Viking.__annotations__.items():
            if k in kwargs:
                setattr(self, k, kwargs.pop(k))
        self.hp = max(1, self.strength)
        self.atk = max(1, self.strength - self.hp)
        self.state = ApproachState

        super().__init__(*args, **kwargs)
    
    @property
    def next_pos(self):
        if not self.target_path:
            return None
        else:
            try:
                return ppb.Vector(self.target_path[self.target_path_step])
            except IndexError:
                return None
    
    @property
    def sprites(self):
        yield from self.parts.values()
    
    def find_next_target(self, scene):
        mushrooms = list(scene.get(tag='mushroom'))
        if mushrooms:
            m = choice(mushrooms)
            start = (round(self.position.x), round(self.position.y))
            end = (round(m.position.x), round(m.position.y))
            pf = next(scene.get(tag='tilemapctrl')).pathfinder

            pf.set_start(start)
            pf.set_end(end)
            pf.score_cells()
            path = pf.follow_path()

            self.target = m
            self.target_path = list(path)
            self.target_path_step = 1 # 0 is the current position

            assert self.target_path[-1] == end, (self.target_path[-1], end)

    def set_state(self, state, scene, signal):
        if self.state != STATES[state]:
            self.last_state_change = time.monotonic()
            self.state = STATES[state]
            self.state.enter_state(self, scene, signal)

    def state_time(self):
        return time.monotonic() - self.last_state_change

    def on_pre_render(self, ev, signal):
        layer = pos_to_layer(self.position)

        # Initialize child sprites on the first frame
        if not self.parts:
            self.parts = {}

            clothes_i = min(len(VIKING_CLOTHES), max(1, self.strength // 2)) - 1
            hat_i = min(len(VIKING_HAT), max(1, self.strength - clothes_i)) - 1

            self.parts['base'] = create_sprite(
                image=VIKING_WALK,
                anchor=self,
                size=2,
            )

            self.parts['clothes'] = create_sprite(
                image=VIKING_CLOTHES[clothes_i],
                anchor=self,
                layer=0.1,
                size=2,
            )

            if self.shield:
                self.parts['hair'] = create_sprite(
                    image=choice(VIKING_HAIR),
                    anchor=self,
                    layer=0.2,
                    size=2,
                )
            else:
                self.parts['hat'] = create_sprite(
                    image=VIKING_HAT[hat_i],
                    anchor=self,
                    layer=0.2,
                    size=2,
                )


            self.parts['corpse'] = create_sprite(
                image=ppb.Image("resources/viking/dead_fg.png"),
                anchor=self,
                layer=0.1,
                size=2,
                opacity=0,
            )

            if self.shield:
                self.parts['shield'] = create_sprite(
                    image=IMAGE_SHIELD,
                    anchor=self,
                    position=ppb.Vector(0.5, 0.0),
                    size=2,
                    layer=0.9,
                )

        self.state.on_pre_render(self, ev, signal)
        self.layer = layer
    
    def on_update(self, ev: Update, signal):
        self.state.on_update(self, ev, signal)

        if self.hp and 'shield' in self.parts:
            s = math.sin(get_time() * 4)
            self.parts['shield'].position = ppb.Vector(0.5, 0.05 - s * 0.1)
    
    def on_cloud_poison(self, ev, signal):
        d = dist(self.position, ev.position)
        if d < 0.5:
            self.size = max(0.0, self.size - 0.1)
    
    def on_mushroom_attack(self, ev, signal):
        self.state.on_mushroom_attack(self, ev, signal)


class VikingSpawnCtrl:
    active: bool = False
    wave_number: int = 0

    @classmethod
    def create(cls, scene):
        ctrl = cls()
        scene.add(ctrl)
        return ctrl
    
    def start(self):
        self.active = True
    
    def spawn_wave(self, scene, signal, count, strength):
        for i in range(count):
            position = self.spawn_position - ppb.Vector(i * 1.5, 0)
            shield_default = self.level.get(f'wave.{self.wave_number}.shield', 0)
            shield = self.level.get(f'wave.{self.wave_number}.{i+1}.shield', shield_default)
            viking = create_sprite(Viking,
                layer=LAYER_GAMEPLAY_LOW,
                position=position,
                strength=strength,
                shield=shield,
                tags=['viking'],
            )
    
    def on_level_loaded(self, ev, signal):
        self.level = ev.level
        try:
            self.spawn_position = ppb.Vector(self.level.find_map_item('VS'))
        except KeyError:
            self.spawn_position = ppb.Vector(-15, 0)

    def on_update(self, ev, signal):
        if self.active:
            vikings = list(ev.scene.get(tag='viking'))
            if not vikings:
                self.wave_number += 1
                # Spawn a new wave, all vikings have died.

                # If the level defines waves, use that. Otherwise, randomize
                # based on wave number.
                if self.level.get('wave.1.count'):
                    try:
                        wave_count = self.level[f'wave.{self.wave_number}.count']
                        wave_strength = self.level[f'wave.{self.wave_number}.strength']
                        self.spawn_wave(ev.scene, signal, wave_count, wave_strength)
                    except KeyError:
                        # If repeating, go back to wave 0
                        if self.level.get('wave.repeat'):
                            self.wave_number = 1
                            wave_count = self.level[f'wave.{self.wave_number}.count']
                            wave_strength = self.level[f'wave.{self.wave_number}.strength']
                            self.spawn_wave(ev.scene, signal, wave_count, wave_strength)
                        else:
                            # I guess... no more vikings?????
                            signal(VikingSpawningDone())

                # Randomize a wave of vikings based on a "danger" level
                else:
                    danger = self.wave_number
                    if danger % 10 == 0:
                        strengths = [danger]
                    else:
                        strengths = []
                        while danger:
                            strength = randint(1, danger)
                            strengths.append(strength)
                            danger -= strength

                    for i, strength in enumerate(strengths * 3):
                        position = self.spawn_position - ppb.Vector(i * 1.5, 0)
                        viking = Viking(
                            layer=LAYER_GAMEPLAY_LOW,
                            position=position,
                            strength=strength,
                        )
                        ev.scene.add(viking, tags=['viking'])
