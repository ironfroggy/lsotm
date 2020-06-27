from dataclasses import dataclass
import random

import ppb

from utils.level import LevelData, LevelLoaded
from utils.spritedepth import pos_to_layer
from utils.pathfinding import AStarPathFinder
from constants import *


class MapItem(ppb.Sprite):
    def __init__(self, *args, **kwargs):
        self.mapitemtype = kwargs.pop('mapitemtype')
        super().__init__(*args, **kwargs)

    # PPB Events
    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position) - 5.0


def make_mapitem(image, rect, mapitemtype):
    def _(x, y):
        t = MapItem(
            image=image,
            position=ppb.Vector(x, y),
            rect=rect,
            layer=LAYER_BACKGROUND+1,
            size=2.0,
            mapitemtype=mapitemtype,
        )
        t.tag = "decor"
        return t
    return _


SOLID = 1
DECOR = 2
GROUND_IMAGES = [
    ppb.Image(f"resources/ground/ground_{r}.png")
    for r in range(6)
]
TREE_H = ppb.Image("resources/ground/tree_horizontal.png")
TREE_V = ppb.Image("resources/ground/tree_vertical.png")
EXIT = ppb.Image("resources/ground/exit.png")

ITEMS = {
    't1': make_mapitem(TREE_V, (0,  0, 32, 32), SOLID),
    't2': make_mapitem(TREE_V, (0, 32, 32, 32), SOLID),
    't3': make_mapitem(TREE_V, (0, 64, 32, 32), SOLID),
    't4': make_mapitem(TREE_H, (0,  0, 32, 32), SOLID),
    't5': make_mapitem(TREE_H, (32, 0, 32, 32), SOLID),
    't6': make_mapitem(TREE_H, (64, 0, 32, 32), SOLID),
    'EX': make_mapitem(EXIT, (0, 0, 32, 32), DECOR),
}


class TilemapCtrl:
    active: bool = False
    width: int = 26
    height: int = 16
    layer: int = LAYER_BACKGROUND

    @classmethod
    def create(cls, scene, signal, **kwargs):
        tc = TilemapCtrl(**kwargs)
        scene.add(tc, tags=['controller', 'tilemapctrl'])
        tc.setup(scene, signal)
        return tc
    
    def __init__(self, width=26, height=16, layer=LAYER_BACKGROUND, images=GROUND_IMAGES):
        self.layer = layer
        self.width = width
        self.height = height
        self.images = images
        self.tiles = []
        self.objects = {}
        self.pathfinder = AStarPathFinder(50)
    
    def setup(self, scene, signal):
        for y in range(-self.height//2, -self.height//2 + self.height):
            for x in range(-self.width//2, -self.width//2 + self.width):
                t = ppb.Sprite(
                    image=random.choice(self.images),
                    position=ppb.Vector(x, y),
                    layer=self.layer,
                    size=1.01,
                )
                self.tiles.append(t)
                scene.add(t)
        
        # Load map objects, which can be:
        # - Decorative items on the map (tree strumps, rocks, etc.)
        # - Mushroom Spawn, marking the place the first mushroom spawns
        # - Exit, marking a spot on the map which ends the level when a mushroom is placed

        level = LevelData(scene.level)
        for cell in level.map_data.values():
            if cell:
                try:
                    factory = ITEMS[cell.code]
                except KeyError:
                    print("Missing item key:", cell.code)
                else:
                    t = factory(cell.x, cell.y)
                    if t:
                        scene.add(t, tags=[t.tag])
                        self.objects[cell.x, cell.y] = t
                        self.pathfinder.block((cell.x, cell.y))
        signal(LevelLoaded(scene.level, level))

    
    def on_key_released(self, ev, signal):
        if self.active:
            if ev.key == ppb.keycodes.Up:
                ev.scene.main_camera.width += 0.05
                print(ev.scene.main_camera.width)
            if ev.key == ppb.keycodes.Down:
                ev.scene.main_camera.width -= 0.05
                print(ev.scene.main_camera.width)
