from dataclasses import dataclass
import math
from time import perf_counter

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update
from ppb.systemslib import System

from constants import COLOR
from easing import out_quad
from events import ScorePoints
from floatingnumbers import CreateFloatingNumber
import tweening
import ui

from cloud import MushroomAttack

from spritedepth import pos_to_layer


@dataclass
class EmitCloud:
    position: ppb.Vector
    cloud_id: int

@dataclass
class PlaceNewMushroom:
    pass


def debounce(obj, marker, delay):
    v = getattr(obj, marker, 0.0)
    t = perf_counter()
    if v + delay < t:
        setattr(obj, marker, t)
        return True
    else:
        return False


class Mushroom(ppb.sprites.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 1.0

    health: int = 10

    smooshed: bool = False
    smoosh_time: float = 0.0
    pressed_time: float = 0.0

    emit_t: float = 0.0
    cloud_id: int = 0
    toxic_radius: float = 0.0
    
    def on_button_pressed(self, ev: ButtonPressed, signal):
        d = (self.position - ev.position).length
        if d < 1.0:
            self.smooshed = True
            self.smoosh_time = 0.0
            self.cloud_id = int(perf_counter() * 1000)
            self.pressed_time = perf_counter()
            self.toxic_radius = 0.5
            tweening.tween(self, "toxic_radius", 1.5, 1.0, easing='out_quad')
    
    def on_button_released(self, ev: ButtonReleased, signal):
        self.smooshed = False

    def on_update(self, ev: Update, signal):
        if self.smooshed:
            self.smoosh_time = min(1.0, self.smoosh_time + ev.time_delta)
            if self.smoosh_time < 0.5:
                if self.emit_t <= 0.0:
                    self.emit_t = 0.1
                    signal(EmitCloud(self.position, self.cloud_id))
                    self.pressed_time = perf_counter()
                else:
                    self.emit_t -= ev.time_delta
            t = out_quad(self.smoosh_time) * 0.2
            self.size = 2.0 * (1.0 - t)
        else:
            self.size = 2.0
        
        if perf_counter() - self.pressed_time <= 1.0:
            if debounce(self, 'apply_toxins', 0.5):
                for viking in ev.scene.get(tag='viking'):
                    d = (viking.position - self.position).length
                    if d <= self.toxic_radius + 0.5:
                        viking.on_mushroom_attack(MushroomAttack(self.cloud_id, viking), signal)

    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position)
    
    def on_viking_attack(self, ev, signal):
        if ev.target is self:
            self.health = max(0, self.health - ev.dmg)
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))
            if self.health <= 0:
                ev.scene.remove(self)


class MushroomPlacementMarker(ppb.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 2.0
    layer: float = 200
    color = COLOR['WHITE']


class MushroomPlacement(System):

    def on_scene_started(self, ev, signal):
        self.mode = "waiting"
        self.marker = MushroomPlacementMarker()
        ev.scene.add(self.marker)
        signal(ui.CreateButton("Mushroom", enabled=False))
        signal(ui.DisableButton("Mushroom"))
    
    def on_score_updated(self, ev, signal):
        if ev.points >= 3:
            signal(ui.EnableButton("Mushroom"))
        else:
            signal(ui.DisableButton("Mushroom"))

    def on_ui_button_pressed(self, ev, signal):
        if ev.label == "Mushroom":
            self.mode = "placing"
            self.marker.size = 2.0
    
    def on_button_released(self, ev, signal):
        if self.mode == "placing" and self.can_place:
            ev.scene.add(Mushroom(
                position=ev.position,
                layer=10,
            ), tags=['mushroom'])
            self.mode = "waiting"
            signal(ScorePoints(-3))
            self.marker.size = 0.0
    
    def on_mouse_motion(self, ev, signal):
        if self.mode == "placing":
            self.marker.position = ev.position
            closest = 100.0
            for mushroom in ev.scene.get(tag='mushroom'):
                d = (mushroom.position - ev.position).length
                closest = min(closest, d)
            if closest >= 1.5:
                self.can_place = True
                self.marker.color = COLOR['GREEN']
            else:
                self.can_place = False
                self.marker.color = COLOR['RED']
