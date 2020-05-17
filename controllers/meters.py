from dataclasses import dataclass

import ppb

from utils.imagesequence import Sequence


@dataclass
class MeterUpdate:
    target: object
    attr: str
    value: float


@dataclass
class MeterRemove:
    target: object
    attr: str = None


class CtrlMeter:
    position: ppb.Vector
    size = 2.0 # Not visible

    def __init__(self, image_seq, target, attr, track):
        self.meter_sprite = ppb.Sprite(
            image=image_seq.copy(),
            position=track.position,
            size=self.size,
            layer=200,
        )
        self.target = target
        self.attr = attr
        self.track = track

    def __image__(self):
        return None

    @classmethod
    def create(cls, scene, *args, **kwargs):
        new = cls(*args, **kwargs)
        new.add_to_scene(scene)

    def add_to_scene(self, scene):
        scene.add(self)
        scene.add(self.meter_sprite)

    def on_pre_render(self, ev, signal):
        self.meter_sprite.position = self.track.position

    def on_meter_update(self, ev: MeterUpdate, signal):
        if self.target == ev.target and self.attr == ev.attr:
            self.meter_sprite.image.set_ratio(ev.value)

    def on_meter_remove(self, ev: MeterRemove, signal):
        if self.target == ev.target and (self.attr == ev.attr or ev.attr is None):
            ev.scene.remove(self.meter_sprite)
            ev.scene.remove(self)
