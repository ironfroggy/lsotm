from random import random

import ppb

from systems.tweening import Tweener
from constants import COLOR


class Particle(ppb.sprites.Sprite):
    image = ppb.Image("resources/sparkle1.png")
    opacity = 128
    opacity_mode = 'add'
    color = COLOR['WHITE']
    size = 2
    rotation = 0

    def __init__(self, *args, **kwargs):
        self.color = kwargs.pop('color', COLOR['WHITE'])
        super().__init__(*args, **kwargs)


class ParticleSystem(ppb.systemslib.System):
    sparkles = []
    index = 0
    size = 100

    @classmethod
    def on_scene_started(cls, ev, signal):
        t = Tweener()
        cls.t = t
        ev.scene.add(t)

        for _ in range(cls.size):
            position = ppb.Vector(random()*12 - 6, random()*12 - 6)
            s = Particle(position=position)
            s.opacity = 0
            s.size = 0
            ev.scene.add(s)
            cls.sparkles.append(s)

    @classmethod
    def spawn(cls, pos, color, heading=None, tsize=2.5):
        s = cls.sparkles[cls.index]
        cls.index = (cls.index + 1) % cls.size
        if color == COLOR_BLACK:
            s.opacity_mode = 'blend'
            s.opacity = 255
        else:
            s.opacity_mode = 'add'
            s.opacity = 128
        s.color = color
        s.position = pos
        s.rotation = randint(0, 260)
        s.size = 1.5
        s.layer = 100
        cls.t.tween(s, 'opacity', 0, 0.5, easing='linear')
        cls.t.tween(s, 'size', tsize, 0.5, easing='linear')
        delay(0.5, lambda: setattr(s, 'size', 0))
        if heading:
            cls.t.tween(s, 'position', heading, 0.5, easing='linear')
