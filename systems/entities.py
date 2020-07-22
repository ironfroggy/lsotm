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
    position: ppb.Vector = ppb.Vector(0, 0)
    anchor: ppb.Sprite = None
    layer: float = 0.0
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


_INSTANCE = None


class SpriteManager(System):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global _INSTANCE
        _INSTANCE = self

    def on_scene_started(self, ev: SceneStarted, signal):
        self.current_scene = ev.scene
        self.signal = signal
    
    def on_pre_render(self, ev: PreRender, signal):
        # Before render, offset the position and layer of children from their parents
        for sprite in ev.scene.get(tag='anchored'):
            sprite.position = sprite.anchor.position + sprite.local_position
            sprite.layer = sprite.anchor.layer + sprite.local_layer

    def on_create_sprite(self, ev: CreateSprite, signal):
        self.create(**vars(ev))
    
    def on_remove_sprite(self, ev: RemoveSprite, signal):
        try:
            ev.scene.remove(ev.sprite)
        except KeyError:
            pass
            # print('Sprite removed twice:', ev.sprite)
        signal(SpriteRemoved(ev.sprite))
    
    def on_sprite_removed(self, ev: SpriteRemoved, signal):
        to_remove = set()
        for sprite in ev.scene.get(tag='anchored'):
            if sprite.anchor is ev.sprite:
                signal(RemoveSprite(sprite))
                to_remove.add(sprite)
        for sprite in to_remove:
            ev.scene.remove(sprite)
    
    def create(self, sprite_class=ppb.Sprite, anchor=None, **kwargs):
        kwargs.setdefault('layer', 0.0)
        kwargs.setdefault('position', ppb.Vector(0, 0))
        kwargs.setdefault('opacity', 255)
        tags = kwargs.pop('tags', [])
        if 'image' in kwargs:
            if isinstance(kwargs['image'], str):
                kwargs['image'] = ppb.Image(kwargs['image'])

        sprite = sprite_class(**kwargs)

        if anchor:
            sprite.anchor = anchor
            sprite.local_position = kwargs['position']
            sprite.local_layer = kwargs['layer']
            tags.append('anchored')

        self.current_scene.add(sprite, tags=tags)
        self.signal(SpriteAdded(sprite))
        return sprite


def create_sprite(*args, **kwargs):
    return _INSTANCE.create(*args, **kwargs)
