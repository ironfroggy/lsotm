from dataclasses import dataclass

import ppb
from ppb.keycodes import Escape
from ppb.events import Quit, StopScene, StartScene
from ppb.assets import Square
from ppb.systemslib import System

from events import *
from systems.text import Text
from ppb_timing import delay

from ppb_tween import tween

import scenes
from constants import *


V = ppb.Vector


@dataclass
class DialogOption:
    option: str


class DialogCtrl:
    active: bool = True
    menu_active = True

    @classmethod
    def create(cls, scene):
        ctrl = cls()
        ctrl.opt_texts = []

        G = 32
        ctrl.bg = ppb.Sprite(
            image=Square(G, G, G),
            size=0.0,
            layer=LAYER_HUD,
            opacity=225,
        )
        scene.add(ctrl.bg)

        ctrl.txt_title = Text(ctrl.title, V(0, 2), layer=LAYER_HUD + 1, size=0.0)
        scene.add(ctrl.txt_title)

        for i, option in enumerate(ctrl.options, 1):
            txt_option = Text(option, V(0, -i), layer=LAYER_HUD + 1, size=0.0)
            scene.add(txt_option)
            ctrl.opt_texts.append(txt_option)

        scene.add(ctrl)
        return ctrl

    def on_toggle_menu(self, ev, signal):
        if self.menu_active:
            self.close_menu()
            signal(CloseMenu())
        else:
            self.open_menu()
            signal(OpenMenu())
    
    def close_menu(self):
        tween(self.bg, 'size', 0.0, 1.0, easing='bounce_out')
        for opt in self.opt_texts:
            tween(opt, 'size', 0.0, 0.5, easing='quad_in')
        tween(self.txt_title, 'size', 0.0, 0.5, easing='quad_in')

        self.menu_active = False
    
    def open_menu(self):
        tween(self.bg, 'size', 8.0, 1.0, easing='bounce_out')
        for opt in self.opt_texts:
            tween(opt, 'size', 2.0, 1.0, easing='bounce_out')
        tween(self.txt_title, 'size', 2.0, 1.0, easing='bounce_out')

        self.menu_active = True

    def on_button_released(self, ev, signal):
        if self.menu_active:
            x = ev.position.x
            y = ev.position.y

            for opt in self.opt_texts:
                dx = abs(x - opt.position.x)
                dy = abs(y - opt.position.y)

                if dy < 0.25 and dx < 1.5:
                    signal(DialogOption(opt.text))
