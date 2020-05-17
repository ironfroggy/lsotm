from dataclasses import dataclass
import math
from time import perf_counter

import ppb
from ppb.events import ButtonPressed, ButtonReleased, Update
from ppb.systemslib import System

from constants import COLOR
from easing import out_quad
from events import ScorePoints

from systems.floatingnumbers import CreateFloatingNumber
from systems import tweening
from systems import ui
from controllers.meters import MeterUpdate, MeterRemove
from controllers.meters import CtrlMeter
from utils.imagesequence import Sequence 
from utils.spritedepth import pos_to_layer
from cloud import MushroomAttack



MUSHROOM_SPRITES = [
    ppb.Image("resources/mushroom/mushroom_0.png"),
    ppb.Image("resources/mushroom/mushroom_1.png"),
    ppb.Image("resources/mushroom/mushroom_2.png"),
    ppb.Image("resources/mushroom/mushroom_3.png"),
]

FRAMES_HEALTH = Sequence("resources/meter/l3_meter_{1..13}.png")
FRAMES_TOXINS = Sequence("resources/meter/l4_meter_{1..13}.png")


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
    image: ppb.Image = MUSHROOM_SPRITES[0]
    size: float = 2.0

    health: int = 10
    toxins: float = 1.0
    cloud: float = 0.0

    # TODO: Can any of these be combined?
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

            # TODO: This is pretty cludging and won't always match the visual clouds
            self.toxic_radius = 0.5
            tweening.tween(self, "toxic_radius", 2.0, 1.0, easing='out_quad')
    
    def on_button_released(self, ev: ButtonReleased, signal):
        self.smooshed = False
        # TODO: Animate the bounce back
        self.image = MUSHROOM_SPRITES[0]

    def on_update(self, ev: Update, signal):
        # If the mushroom is being smooshed and it has toxins to squish...
        if self.toxins and self.smooshed:

            # Set smoosh frame
            i = tweening.lerp(0, 3, out_quad(self.smoosh_time * 2.0))
            self.image = MUSHROOM_SPRITES[i]

            # Accumulate cloud counter from toxin counter
            self.smoosh_time = min(1.0, self.smoosh_time + ev.time_delta)
            self.toxins = max(0.0, self.toxins - ev.time_delta)
            self.cloud = self.cloud + ev.time_delta
            signal(MeterUpdate(self, 'toxins', self.toxins))

            # If the cloud accumulator reaches threashold,
            # emit clouds and clear the accumulator.
            if self.cloud >= 0.25:
                signal(EmitCloud(self.position, self.cloud_id))
                self.pressed_time = perf_counter()
                self.cloud -= 0.25

        # If the mushroom isn't being smooshed, increase toxin accumulator
        # and reset the cloud accumulator.
        elif not self.smooshed:
            self.toxins = min(1.0, self.toxins + ev.time_delta * 0.5)
            self.cloud = 0.0
            signal(MeterUpdate(self, 'toxins', self.toxins))

        # If the mushroom has been pressed for less than a second, apply
        # toxin damage every 0.25 seconds within the toxin radius.
        if perf_counter() - self.pressed_time <= 1.0:
            if debounce(self, 'apply_toxins', 0.25):
                for viking in ev.scene.get(tag='viking'):
                    d = (viking.position - self.position).length
                    if d <= self.toxic_radius + 0.5:
                        viking.on_mushroom_attack(MushroomAttack(perf_counter(), viking), signal)

    def on_pre_render(self, ev, signal):
        self.layer = pos_to_layer(self.position)

    def on_viking_attack(self, ev, signal):
        if ev.target is self:
            self.health = max(0, self.health - ev.dmg)
            signal(CreateFloatingNumber(-1, self.position, (255, 0, 0)))
            signal(MeterUpdate(self, 'health', self.health / 10))
            if self.health <= 0:
                ev.scene.remove(self)
                signal(MeterRemove(self))


class MushroomPlacementMarker(ppb.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 0.0
    layer: float = 200
    color = COLOR['WHITE']


class MushroomPlacement(System):
    """The Mushroom Placement System is responsible for:
    - Invoking the UI elements for selecting new units to place
    - Allowing the user to place new units
    - Initializing the scene with the first units for a level

    The system listens to these events:
    - SceneStarted
    - ScoreUpdated
    - UIButtonPressed
    - ButtonReleased
    - MouseMotion

    The system sends these events:
    - ScorePoints
    - CreateButton
    - EnableButton
    - DisableButton
    - MeterUpdate
    """

    # TODO: Create mushrooms through events
    def create_mushroom(self, position, signal):
        mushroom = Mushroom(position=position, layer=10)
        self.scene.add(mushroom, tags=['mushroom'])
        # TODO: Create meters through events
        CtrlMeter.create(self.scene, FRAMES_HEALTH, target=mushroom, attr='health', track=mushroom)
        CtrlMeter.create(self.scene, FRAMES_TOXINS, target=mushroom, attr='toxins', track=mushroom)
        signal(MeterUpdate(mushroom, 'health', 1.0))

    def on_scene_started(self, ev, signal):
        self.scene = ev.scene
        self.mode = "waiting"
        self.marker = MushroomPlacementMarker()
        ev.scene.add(self.marker)
        signal(ui.CreateButton("Mushroom", enabled=False))
        signal(ui.DisableButton("Mushroom"))

        self.create_mushroom(ppb.Vector(0, 0), signal)
    
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
            self.create_mushroom(ev.position, signal)
            self.mode = "waiting"
            signal(ScorePoints(-3))
            self.marker.size = 0.0
    
    def on_mouse_motion(self, ev, signal):
        self.marker.position = ev.position
        if self.mode == "placing":
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
