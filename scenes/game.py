import ppb
from ppb.events import *

from controllers.unitplacement import UnitPlacementCtrl
from controllers.tilemap import TilemapCtrl
from controllers.scoring import ScoreCtrl
from viking import VikingSpawnCtrl

from controllers.dialog import DialogCtrl, DialogOption
from scenes.paused import PausedScene
from constants import *
from events import *

from ppb_timing import delay


class GameOverDialog(DialogCtrl):
    title = "Game Over!"

    options = (
        'restart',
        'quit',
    )

    def on_dialog_option(self, ev: DialogOption, signal):
        if ev.option == 'restart':
            signal(StopScene())
            delay(0, lambda: signal(RestartGame()))
        elif ev.option == 'quit':
            signal(Quit())


class GameScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def __init__(self, level):
        super().__init__()
        self.level = level
        self.game_over_dialog = GameOverDialog.create(self)

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
    
    def on_mushroom_death(self, ev, signal):
        remaining = list(ev.scene.get(tag='mushroom'))
        if not remaining:
            signal(GameOver())
            self.game_over_dialog.open_menu()
