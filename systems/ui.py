from dataclasses import dataclass
import math

import ppb
from ppb.systemslib import System

from systems import text
from constants import *


def dist(v1, v2):
    a = abs(v1.x - v2.x) ** 2
    b = abs(v1.y - v2.y) ** 2
    return math.sqrt(a + b)


@dataclass
class CreateButton:
    """Event to request button creation."""

    label: str
    enabled: bool = True

@dataclass
class DisableButton:
    """Event to request a button be disabled."""

    label: str

@dataclass
class EnableButton:
    """Event to request a button be disabled."""

    label: str

@dataclass
class UIButtonPressed:
    """Event published when a button is pressed."""

    label: str


class UIButton(ppb.Sprite):
    image = ppb.Image("resources/uibutton.png")
    size = 2.0
    label: str
    enabled: bool = True

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label')
        super().__init__(*args, **kwargs)
        if not self.enabled:
            self.enabled = 128

    def on_disable_button(self, ev, signal):
        if ev.label == self.label:
            self.enabled = False
            self.opacity = 128

    def on_enable_button(self, ev, signal):
        if ev.label == self.label:
            self.enabled = True
            self.opacity = 255


@dataclass
class DebugMessage:
    msg: str


# TODO: Clear elements when scene ends / handle different scenes
# Become a controller? Not sure yet.
class UISystem(System):
  
    def on_scene_started(self, ev, signal):
        self.ui_elements = {}

    def on_create_button(self, ev, signal):
        if ev.label in self.ui_elements:
            try:
                ev.scene.remove(self.ui_elements[ev.label])
            except KeyError:
                pass
            del self.ui_elements[ev.label]

        element = UIButton(label=ev.label, enabled=ev.enabled)
        element.position = ppb.Vector(-5 + len(self.ui_elements) * 2.0, 5)
        element.layer = LAYER_HUD
        ev.scene.add(element)
        self.ui_elements[ev.label] = element

        label = text.Text(ev.label, position=element.position, size=1.0, layer=LAYER_HUD+1)
        label.scene = ev.scene
        ev.scene.add(label)
        label.setup()
    
    def on_button_released(self, ev, signal):
        for element in self.ui_elements.values():
            if element.enabled:
                d = dist(element.position, ev.position)
                if d < 0.5:
                    signal(UIButtonPressed(element.label))
    
    def on_debug_message(self, ev, signal):
        print('DEBUG', ev.msg)
