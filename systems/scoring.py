import ppb
from ppb.systemslib import System

from systems.text import Text
from constants import COLOR


class ScoreBoard(System):
    
    @classmethod
    def on_scene_started(cls, ev, signal):
        cls.score = 0
        cls.text = Text(str(cls.score), ppb.Vector(0, 4), color=COLOR['YELLOW'])
        ev.scene.add(cls.text)
    
    @classmethod
    def on_score_points(cls, ev, signal):
        cls.score += ev.points
        cls.text.text = str(cls.score)
        signal(ScoreUpdated(cls.score))
    
    @classmethod
    def on_score_set(cls, ev, signal):
        cls.score = ev.points
        cls.text.text = str(cls.score)
        signal(ScoreUpdated(cls.score))
