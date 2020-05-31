from dataclasses import dataclass
from random import random, randint, uniform
import typing

import ppb

from ppb_tween import Tweener

from constants import COLOR
from systems.timer import delay, repeat


# TODO: what is the advantage of an event over a simple exported function?
@dataclass
class ParticleSpawnerCreate:
    source: typing.Tuple[ppb.Vector, ppb.Vector]
    dest: typing.Tuple[ppb.Vector, ppb.Vector]
    color: ppb.utils.Color
    lifespan: float
    frequency: float = 0.025
    opacity: int = 255
    opacity_mode: ppb.flags.BlendMode = ppb.flags.BlendModeBlend


class Particle(ppb.sprites.Sprite):
    image = ppb.Image("resources/sparkle1.png")
    opacity = 128
    opacity_mode = 'add'
    tint = COLOR['WHITE']
    size = 2
    rotation = 0

    def __init__(self, *args, **kwargs):
        self.tint = kwargs.pop('color', COLOR['WHITE'])
        super().__init__(*args, **kwargs)


class ParticleSystem(ppb.systemslib.System):
    size = 250

    @classmethod
    def on_scene_started(cls, ev, signal):
        cls.scene = ev.scene
        t = Tweener()
        cls.t = t
        ev.scene.add(t)
        ev.scene.__particle_pool = []
        ev.scene.__particle_pool_index = 0

        for _ in range(cls.size):
            position = ppb.Vector(random()*12 - 6, random()*12 - 6)
            s = Particle(position=position)
            s.opacity = 0
            s.size = 0
            ev.scene.add(s)
            ev.scene.__particle_pool.append(s)

    @classmethod
    def spawn(cls, pos, color, heading=None, sizing=(0.1, 0.1), opacity=None, opacity_mode=None):
        i = cls.scene.__particle_pool_index
        s = cls.scene.__particle_pool[i]
        cls.scene.__particle_pool_index = (i + 1) % cls.size
        if color == COLOR['BLACK']:
            s.opacity_mode = opacity_mode or ppb.flags.BlendModeBlend
            s.opacity = opacity or 255
        else:
            s.opacity_mode = opacity_mode or ppb.flags.BlendModeAdd
            s.opacity = opacity or 128
        s.tint = color
        s.position = pos
        s.rotation = randint(0, 260)
        s.size = sizing[0]
        s.layer = 1000
        cls.t.tween(s, 'opacity', 0, 0.5, easing='cubic_in')
        cls.t.tween(s, 'size', sizing[1], 0.5, easing='linear')
        if heading:
            cls.t.tween(s, 'position', heading, 0.5, easing='linear')

    def on_particle_spawner_create(self, ev: ParticleSpawnerCreate, signal):
        source_bl, source_tr = ev.source
        dest_bl, dest_tr = ev.dest

        def spawn_one():
            source_x = uniform(source_bl.x, source_tr.x)
            source_y = uniform(source_bl.y, source_tr.y)
            dest_x = uniform(dest_bl.x, dest_tr.x)
            dest_y = uniform(dest_bl.y, dest_tr.y)

            source = ppb.Vector(source_x, source_y)
            dest = ppb.Vector(dest_x, dest_y)

            ParticleSystem.spawn(source, ev.color, dest,
                opacity=ev.opacity, opacity_mode=ev.opacity_mode,
            )
        
        repeat(ev.frequency, spawn_one, ev.lifespan)
