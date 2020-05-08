from dataclasses import dataclass
import math

import ppb
from ppb.systemslib import System



LAYER = 500

def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


@dataclass
class CreateButton:
    label: str
    event: object


class UIButton(ppb.Sprite):
    label: str
    event: object

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label')
        self.event = kwargs.pop('event')
        super().__init__(*args, **kwargs)


@dataclass
class DebugMessage:
    msg: str


class UISystem(System):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui_elements = []

    def on_create_button(self, ev, signal):
        element = UIButton(label=ev.label, event=ev.event)
        element.position = ppb.Vector(-5 + len(self.ui_elements), 5)
        ev.scene.add(element)
        self.ui_elements.append(element)
    
    def on_button_released(self, ev, signal):
        for element in self.ui_elements:
            d = dist(element.position, ev.position)
            if d < 0.5:
                print('click', element.label)
                signal(element.event)
    
    def on_debug_message(self, ev, signal):
        print('DEBUG', ev.msg)
    
    # def on_scene_started(self, ev, signal):
    #     signal(CreateButton("Button 1", DebugMessage("clicked button 1")))
    #     signal(CreateButton("Button 2", DebugMessage("clicked button 2")))
