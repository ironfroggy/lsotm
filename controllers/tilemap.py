import random

import ppb


class TilemapInitialization:
    pass


class TilemapCtrl:
    active: bool = False
    width: int = 26
    height: int = 16

    @classmethod
    def create(cls, scene):
        tc = TilemapCtrl()

        for y in range(-cls.height//2, -cls.height//2 + cls.height):
            for x in range(-cls.width//2, -cls.width//2 + cls.width):
                r = random.randint(0, 5)
                t = ppb.Sprite(
                    image=ppb.Image(f"resources/ground/ground_{r}.png"),
                    position=ppb.Vector(x, y),
                    layer=-1,
                    size=1.01
                )
                scene.add(t)

        return tc
    
    def on_key_released(self, ev, signal):
        if self.active:
            if ev.key == ppb.keycodes.Up:
                ev.scene.main_camera.width += 0.05
                print(ev.scene.main_camera.width)
            if ev.key == ppb.keycodes.Down:
                ev.scene.main_camera.width -= 0.05
                print(ev.scene.main_camera.width)
