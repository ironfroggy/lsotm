import ppb
from ppb.keycodes import Escape
from ppb.events import Quit, StopScene, StartScene
from ppb.assets import Square
from ppb.systemslib import System

from events import *
from systems.text import Text
from systems.timer import delay

from ppb_tween import tween

import scenes


V = ppb.Vector

MENU_LAYER = 1000


class DialogCtrl:
    active: bool = True
    menu_active = True

    @classmethod
    def create(cls, scene, signal):
        ctrl = cls()

        G = 32
        ctrl.bg = ppb.Sprite(
            image=Square(G, G, G),
            size=0.0,
            layer=MENU_LAYER,
            opacity=225,
        )
        scene.add(ctrl.bg)

        ctrl.title = Text('Last Stand of the Mushrooms', V(0, 2), layer=MENU_LAYER + 1, size=0.0)
        scene.add(ctrl.title)

        ctrl.opt_start = Text('resume', V(0, -1), layer=MENU_LAYER + 1, size=0.0)
        scene.add(ctrl.opt_start)

        ctrl.opt_restart = Text('restart', V(0, -2), layer=MENU_LAYER + 1, size=0.0)
        scene.add(ctrl.opt_restart)

        ctrl.opt_quit = Text('quit', V(0, -3), layer=MENU_LAYER + 1, size=0.0)
        scene.add(ctrl.opt_quit)

        # TODO: Make this configurable
        ctrl.options = (
            (ctrl.opt_start, lambda: signal(StopScene())),
            (ctrl.opt_restart, lambda: ctrl.restart_game(signal)),
            (ctrl.opt_quit, lambda: signal(Quit())),
        )

        scene.add(ctrl)
        return ctrl
    
    def restart_game(self, signal):
        signal(StopScene())
        delay(0, lambda: signal(RestartGame()))

    # TODO: Probably drop?
    def on_start_game(self, ev, signal):
        self.close_menu()
    
    def on_player_death(self, ev, signal):
        self.open_menu()

    def on_toggle_menu(self, ev, signal):
        if self.menu_active:
            self.close_menu()
            signal(CloseMenu())
        else:
            self.open_menu()
            signal(OpenMenu())
    
    def close_menu(self):
        tween(self.bg, 'size', 0.0, 1.0, easing='bounce_out')
        tween(self.opt_start, 'size', 0.0, 0.5, easing='quad_in')
        tween(self.opt_restart, 'size', 0.0, 0.5, easing='quad_in')
        tween(self.opt_quit, 'size', 0.0, 0.5, easing='quad_in')
        tween(self.title, 'size', 0.0, 0.5, easing='quad_in')

        self.menu_active = False
    
    def open_menu(self):
        tween(self.bg, 'size', 8.0, 1.0, easing='bounce_out')
        tween(self.opt_start, 'size', 2.0, 1.0, easing='bounce_out')
        tween(self.opt_restart, 'size', 2.0, 1.0, easing='bounce_out')
        tween(self.opt_quit, 'size', 2.0, 1.0, easing='bounce_out')
        tween(self.title, 'size', 2.0, 1.0, easing='bounce_out')

        self.menu_active = True

    def on_button_released(self, ev, signal):
        if self.menu_active:
            x = ev.position.x
            y = ev.position.y

            for opt, callback in self.options:
                dx = abs(x - opt.position.x)
                dy = abs(y - opt.position.y)

                if dy < 0.25 and dx < 1.5:
                    callback()
