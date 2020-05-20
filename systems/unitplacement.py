import ppb

from constants import COLOR
from controllers.meters import CtrlMeter
from mushroom import Smooshroom
from systems import ui
from utils.imagesequence import Sequence 
from controllers.meters import MeterUpdate, MeterRemove
from events import ScorePoints, ScoreUpdated


FRAMES_HEALTH = Sequence("resources/meter/l3_meter_{1..13}.png")
FRAMES_TOXINS = Sequence("resources/meter/l4_meter_{1..13}.png")


class MushroomPlacementMarker(ppb.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 0.0
    layer: float = 200
    color = COLOR['WHITE']


class MushroomPlacement(ppb.systemslib.System):
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
        # TODO: create different kinds
        mushroom = Smooshroom(position=position, layer=10)
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
