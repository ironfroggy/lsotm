import ppb

from controllers.unitplacement import UnitPlacementCtrl
from controllers.tilemap import TilemapCtrl
from controllers.scoring import ScoreCtrl
from viking import VikingSpawnCtrl

from constants import COLOR
from scenes.paused import PausedScene
from ppb_timing import delay


class GameScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def __init__(self, level):
        super().__init__()
        self.level = level

    def on_scene_started(self, ev, signal):
        self.setup_scene(ev.scene, signal)
    
    def setup_scene(self, scene, signal):
        TilemapCtrl.create(scene)
        ScoreCtrl.create(scene)
        UnitPlacementCtrl.create(scene, signal)

        viking_ctrl = VikingSpawnCtrl.create(scene)
        delay(1, viking_ctrl.start)

    def on_key_released(self, ev, signal):
        if ev.key == ppb.keycodes.Escape:
            signal(ppb.events.StartScene(PausedScene))
    
    def on_restart_game(self, ev, signal):
        signal(ppb.events.StopScene())
