from dataclasses import dataclass
import typing

import ppb
from ppb.systemslib import System
from ppb.events import *

from constants import *
from events import *


@dataclass
class SpriteAdded:
    sprite: ppb.Sprite

@dataclass
class SpriteRemoved:
    sprite: ppb.Sprite

@dataclass
class CreateSprite:
    image: typing.Union[str, ppb.Image]
    position: ppb.Vector
    anchor: ppb.Sprite = None
    layer: float = None
    size: float = 1.0
    opacity: int = 255
    sprite_class: type = ppb.Sprite

@dataclass
class RemoveSprite:
    sprite: ppb.Sprite


@dataclass
class Anchor:
    parent: ppb.Sprite
    child: ppb.Sprite
    position: ppb.Vector
    layer: float = 0.0

    def __hash__(self):
        return hash((
            self.parent,
            self.child,
            self.position.x,
            self.position.y,
            self.layer,
        ))


class SpriteManager(System):

    def on_scene_started(self, ev: SceneStarted, signal):
        ev.scene.__anchors = set()
    
    def on_pre_render(self, ev: PreRender, signal):
        for anchor in ev.scene.__anchors:
            anchor.child.position = anchor.parent.position + anchor.position
            anchor.child.layer = anchor.parent.layer + anchor.layer

    def on_create_sprite(self, ev: CreateSprite, signal):
        if isinstance(ev.image, str):
            image = ppb.Image(ev.image)
        else:
            image = ev.image
        
        sprite = ev.sprite_class(
            image=image,
            position=ev.position,
            layer=ev.layer,
            size=ev.size,
            opacity=ev.opacity,
        )

        if ev.anchor:
            anchor = Anchor(ev.anchor, sprite, ev.position, ev.layer)
            ev.scene.__anchors.add(anchor)

        ev.scene.add(sprite)
        signal(SpriteAdded(sprite))
    
    def on_remove_sprite(self, ev: RemoveSprite, signal):
        ev.scene.remove(ev.sprite)
        signal(SpriteRemoved(ev.sprite))
    
    def on_sprite_removed(self, ev: SpriteRemoved, signal):
        to_remove = set()
        for anchor in ev.scene.__anchors:
            if anchor.parent == ev.sprite:
                signal(RemoveSprite(anchor.child))
                to_remove.add(anchor)
        for anchor in to_remove:
            ev.scene.__anchors.remove(anchor)
