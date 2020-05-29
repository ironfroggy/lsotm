import random

import ppb


class TilemapInitialization:
    pass

TILE_IMAGES = [
    ppb.Image(f"resources/ground/ground_{r}.png")
    for r in range(6)
]


class TilemapCtrl:
    active: bool = False
    width: int = 26
    height: int = 16
    layer: int = -1

    @classmethod
    def create(cls, scene, **kwargs):
        tc = TilemapCtrl(**kwargs)
        scene.add(tc)
        tc.setup(scene)
        return tc
    
    def __init__(self, width=26, height=16, layer=-1, images=TILE_IMAGES):
        self.layer = layer
        self.width = width
        self.height = height
        self.images = images
        self.tiles = []
    
    def setup(self, scene):
        for y in range(-self.height//2, -self.height//2 + self.height):
            for x in range(-self.width//2, -self.width//2 + self.width):
                t = ppb.Sprite(
                    image=random.choice(self.images),
                    position=ppb.Vector(x, y),
                    layer=self.layer,
                    size=1.01
                )
                self.tiles.append(t)
                scene.add(t)
    
    def on_key_released(self, ev, signal):
        if self.active:
            if ev.key == ppb.keycodes.Up:
                ev.scene.main_camera.width += 0.05
                print(ev.scene.main_camera.width)
            if ev.key == ppb.keycodes.Down:
                ev.scene.main_camera.width -= 0.05
                print(ev.scene.main_camera.width)
