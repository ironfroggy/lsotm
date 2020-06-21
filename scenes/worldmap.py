import ppb

from constants import COLOR
from ppb.events import StartScene
from scenes.game import GameScene

PIN_COORDS = [
    (-7.3, -3.4),
    (-5.4, -3.4),
    (-4.25, -2.45),
    (-6, -1),
    (-3, 1),
    (-2, 1),
    (-1, 1),
    (1.3, 0.25),
    (1.3, -1),
    (2.75, -0.75),
    (3.75, 0.25),
    (4.75, 1.25),
    (6.0, 1.25),
    (7.0, 2.5),
    (8.0, 4.0),
]


class WorldmapScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def on_scene_started(self, ev, signal):
        logo = ppb.Sprite(
            image=ppb.Image("resources/worldmap.png"),
            size=10,
            layer=1,
        )
        ev.scene.add(logo)

        self.pins = []
        for c in PIN_COORDS:
            pin = ppb.Sprite(
                image=ppb.Image("resources/worldmap_pin.png"),
                size=2,
                position=ppb.Vector(*c),
                tint=COLOR['RED'],
                layer=2,
            )
            ev.scene.add(pin)
            self.pins.append(pin)
    
    # def on_key_released(self, ev, signal):
    #     signal(StartScene(GameScene))
    
    def on_button_released(self, ev, signal):
        for i, pin in enumerate(self.pins, 1):
            d = (pin.position - ev.position).length
            if d < 0.5:
                signal(StartScene(GameScene(i)))
