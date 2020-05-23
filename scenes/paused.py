import ppb

from constants import COLOR
from controllers.dialog import DialogCtrl


class PausedScene(ppb.BaseScene):
    background_color = COLOR['BLACK']

    def on_scene_started(self, ev, signal):
        self.dialog = DialogCtrl.create(ev.scene, signal)
        self.dialog.open_menu()
    
    def on_key_released(self, ev: ppb.events.KeyReleased, signal):
        if ev.key == ppb.keycodes.Escape:
            signal(ppb.events.StopScene())
