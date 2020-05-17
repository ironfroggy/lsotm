import random

import ppb


class TilemapSystem(ppb.systemslib.System):
    width: int = 25
    height: int = 16

    def on_scene_started(self, ev, signal):
        for y in range(-self.height//2, -self.height//2 + self.height):
            for x in range(-self.width//2, -self.width//2 + self.width):
                r = random.randint(0, 5)
                t = ppb.Sprite(
                    image=ppb.Image(f"resources/ground/ground_{r}.png"),
                    position=ppb.Vector(x, y),
                    layer=-1,
                )
                ev.scene.add(t)
    
    def on_key_released(self, ev, signal):
        if ev.key == ppb.keycodes.Up:
            ev.scene.main_camera.width += 0.05
            print(ev.scene.main_camera.width)
        if ev.key == ppb.keycodes.Down:
            ev.scene.main_camera.width -= 0.05
            print(ev.scene.main_camera.width)
