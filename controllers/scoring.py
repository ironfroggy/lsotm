import ppb
from ppb.systemslib import System

from events import ScoreUpdated
from systems.text import Text
from constants import COLOR


class ScoreCtrl:

    @classmethod
    def create(cls, scene, signal):
        ctrl = cls()
        ctrl.score = 0
        ctrl.text = Text(str(ctrl.score), ppb.Vector(0, 4), color=COLOR['YELLOW'])
        scene.add(ctrl.text)
        scene.add(ctrl)
        return ctrl
    
    def __init__(self):
        self.score = 0
    
    def on_score_points(self, ev, signal):
        self.score += ev.points
        self.text.text = str(self.score)
        signal(ScoreUpdated(self.score))
    
    def on_score_set(self, ev, signal):
        self.score = ev.points
        self.text.text = str(self.score)
        signal(ScoreUpdated(self.score))
