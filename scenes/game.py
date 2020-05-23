import ppb

from controllers.unitplacement import UnitPlacementCtrl
from controllers.tilemap import TilemapCtrl
from controllers.scoring import ScoreCtrl
from controllers.dialog import DialogCtrl
from viking import VikingSpawnCtrl


class GameScene(ppb.BaseScene):

    def on_scene_started(self, ev, signal):
        TilemapCtrl.create(ev.scene)
        VikingSpawnCtrl.create(ev.scene)
        ScoreCtrl.create(ev.scene)
        UnitPlacementCtrl.create(ev.scene, signal)
        DialogCtrl.create(ev.scene, signal)
