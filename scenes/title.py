import ppb

from constants import COLOR
from ppb.events import StartScene
from scenes.game import GameScene


class TitleScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def on_scene_started(self, ev, signal):
        logo = ppb.Sprite(
            image=ppb.Image("resources/logo.png"),
            size=10,
        )
        ev.scene.add(logo)
    
    def on_key_released(self, ev, signal):
        signal(StartScene(GameScene))