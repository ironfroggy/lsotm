import ppb

from constants import COLOR
from controllers.meters import CtrlMeter
from systems import ui
from utils.imagesequence import Sequence 
from controllers.meters import MeterUpdate, MeterRemove
from events import ScorePoints, ScoreUpdated

from mushroom import Smooshroom, Poddacim

FRAMES_HEALTH = Sequence("resources/meter/l3_meter_{1..13}.png")
FRAMES_TOXINS = Sequence("resources/meter/l4_meter_{1..13}.png")


class MushroomPlacementMarker(ppb.Sprite):
    image: ppb.Image = ppb.Image("resources/mushroom/mushroom_0.png")
    size: float = 0.0
    layer: float = 200
    tint = COLOR['WHITE']


class UnitPlacementCtrl:
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

    active: bool = True

    @classmethod
    def create(cls, scene, signal):
        ctrl = cls()

        ctrl.scene = scene
        ctrl.mode = "waiting"
        ctrl.marker = MushroomPlacementMarker()
        scene.add(ctrl.marker)
        
        signal(ui.CreateButton("Smooshroom", enabled=False))
        signal(ui.DisableButton("Smooshroom"))

        signal(ui.CreateButton("Poddacim", enabled=False))
        signal(ui.DisableButton("Poddacim"))

        # TODO: Move to scene?
        ctrl.create_mushroom(Smooshroom, ppb.Vector(0, 0), signal)

        scene.add(ctrl)
        return ctrl

    # TODO: Create mushrooms through events
    def create_mushroom(self, cls, position, signal):
        # TODO: create different kinds
        mushroom = cls(position=position, layer=10)
        self.scene.add(mushroom, tags=['mushroom'])
        # TODO: Create meters through events
        CtrlMeter.create(self.scene, FRAMES_HEALTH, target=mushroom, attr='health', track=mushroom)
        CtrlMeter.create(self.scene, FRAMES_TOXINS, target=mushroom, attr='toxins', track=mushroom)
        signal(MeterUpdate(mushroom, 'health', 1.0))
    
    def on_score_updated(self, ev, signal):
        if ev.points >= 3:
            signal(ui.EnableButton("Smooshroom"))
            signal(ui.EnableButton("Poddacim"))
        else:
            signal(ui.DisableButton("Smooshroom"))
            signal(ui.DisableButton("Poddacim"))

    def on_ui_button_pressed(self, ev, signal):
        if ev.label == "Smooshroom":
            self.mode = "placing"
            self.place_type = Smooshroom
            self.marker.size = 2.0
            self.marker.image = self.place_type.smoosh_sprites[0]
        if ev.label == "Poddacim":
            self.mode = "placing"
            self.place_type = Poddacim
            self.marker.size = 2.0
            self.marker.image = self.place_type.smoosh_sprites[0]
    
    def on_button_released(self, ev, signal):
        if self.mode == "placing" and self.can_place:
            self.create_mushroom(self.place_type, ev.position, signal)
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
                self.marker.tint = (0, 255, 0, 128) # COLOR['GREEN']
            else:
                self.can_place = False
                self.marker.tint = COLOR['RED']
