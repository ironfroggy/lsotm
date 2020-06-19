import ppb
from ppb.events import *

from constants import COLOR
from controllers.dialog import DialogCtrl, DialogOption
from events import *

from ppb_timing import delay


class PauseDialog(DialogCtrl):
    title = "Last Stand of the Mushrooms"

    options = (
        'resume',
        'restart',
        'quit',
    )

    def on_dialog_option(self, ev: DialogOption, signal):
        if ev.option == 'resume':
            signal(StopScene())
        elif ev.option == 'restart':
            signal(StopScene())
            delay(0, lambda: signal(RestartGame()))
        elif ev.option == 'quit':
            signal(Quit())


class PausedScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def on_scene_started(self, ev, signal):
        self.dialog = PauseDialog.create(ev.scene)
        self.dialog.open_menu()
    
    def on_key_released(self, ev: ppb.events.KeyReleased, signal):
        if ev.key == ppb.keycodes.Escape:
            signal(ppb.events.StopScene())
