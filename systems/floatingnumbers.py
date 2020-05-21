from dataclasses import dataclass
import typing

import ppb
from ppb.systemslib import System

from systems.text import Text

from ppb_tween import tween


@dataclass
class CreateFloatingNumber:
    number: int
    position: ppb.Vector
    color: typing.Tuple[int, int, int]


class FloatingNumberSystem(System):

    def on_create_floating_number(self, ev: CreateFloatingNumber, signal):
        T = Text(str(ev.number), ev.position, color=ev.color, layer=500)
        ev.scene.add(T)
        T.scene = ev.scene
        T.setup()
        tween(T, 'position', ev.position + ppb.Vector(0, -1), 0.5)
        tween(T, 'opacity', 0, 0.5)
