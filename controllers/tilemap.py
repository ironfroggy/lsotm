from dataclasses import dataclass
import random

import ppb

from utils.spritedepth import pos_to_layer
from constants import *


class TilemapInitialization:
    pass


@dataclass
class MapCell:
    x: int
    y: int
    code: str


@dataclass
class RoutePoint:
    n: int
    approach_distance: float = 0.0

    def __hash__(self):
        return hash(("routepoint", id(self)))
    
    def __repr__(self):
        return f"<RoutePoint n={self.n}>"


class Decoration(ppb.Sprite):
    # PPB Events
    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position) - 5.0


def make_decor(image, rect):
    def _(x, y):
        t = Decoration(
            image=image,
            position=ppb.Vector(x, y),
            rect=rect,
            layer=LAYER_BACKGROUND+1,
            size=2.0,
        )
        t.tag = "decor"
        return t
    return _

def make_routepoint(n):
    def _(x, y):
        t = RoutePoint(n)
        t.health = None
        t.position = ppb.Vector(x, y)
        t.tag = "routepoint"
        return t
    return _


GROUND_IMAGES = [
    ppb.Image(f"resources/ground/ground_{r}.png")
    for r in range(6)
]

TREE_H = ppb.Image("resources/ground/tree_horizontal.png")
TREE_V = ppb.Image("resources/ground/tree_vertical.png")


MAP = """
t1 -- t4 t5 t6 -- --
t2 P1 -- P2 -- -- --
t3 -- t1 -- -- -- --
-- P0 t2 MS -- -- --
t1 -- t3 -- -- -- --
t2 P1 -- P2 -- -- --
t3 -- t4 t5 t5 t6 --
"""

ITEMS = {
    't1': make_decor(TREE_V, (0,  0, 32, 32)),
    't2': make_decor(TREE_V, (0, 32, 32, 32)),
    't3': make_decor(TREE_V, (0, 64, 32, 32)),
    't4': make_decor(TREE_H, (0,  0, 32, 32)),
    't5': make_decor(TREE_H, (32, 0, 32, 32)),
    't6': make_decor(TREE_H, (64, 0, 32, 32)),
}
for n in range(10):
    ITEMS[f'P{n}'] = make_routepoint(n)


def parse_map(map_str):
    lines = MAP.strip().split('\n')
    map_width = len(lines[0].split())
    map_height = len(lines)
    rows = map_str.strip().split('\n')
    map = {}
    for i, row in enumerate(rows):
        for j, code in enumerate(row.split()):
            x, y = j-map_width//2, -i+map_height//2
            if code == '--':
                cell = None
            else:
                cell = MapCell(x, y, code)
            map[x, y] = cell
    return map


class TilemapCtrl:
    active: bool = False
    width: int = 26
    height: int = 16
    layer: int = LAYER_BACKGROUND

    @classmethod
    def create(cls, scene, **kwargs):
        tc = TilemapCtrl(**kwargs)
        scene.add(tc)
        tc.setup(scene)
        return tc
    
    def __init__(self, width=26, height=16, layer=LAYER_BACKGROUND, images=GROUND_IMAGES):
        self.layer = layer
        self.width = width
        self.height = height
        self.images = images
        self.tiles = []
        self.objects = {}
    
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
        
        # Load map objects, which can be:
        # - Decorative items on the map (tree strumps, rocks, etc.)
        # - Route Points, marking the path vikings take through the level
        # - Mushroom Spawn, marking the place the first mushroom spawns
        # - Exit, marking a spot on the map which ends the level when a mushroom is placed

        for cell in parse_map(MAP).values():
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
    
    def on_key_released(self, ev, signal):
        if self.active:
            if ev.key == ppb.keycodes.Up:
                ev.scene.main_camera.width += 0.05
                print(ev.scene.main_camera.width)
            if ev.key == ppb.keycodes.Down:
                ev.scene.main_camera.width -= 0.05
                print(ev.scene.main_camera.width)
