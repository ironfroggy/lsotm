from dataclasses import dataclass
from time import monotonic

import ppb
from ppb.systemslib import System

import easing

def ilerp(f1, f2, t):
    return int(f1 + t * (f2 - f1))

def flerp(f1, f2, t):
    return f1 + t * (f2 - f1)

def vlerp(v1, v2, t):
    return ppb.Vector(
        v1.x + t * (v2.x - v1.x),
        v1.y + t * (v2.y - v1.y),
    )

def tlerp(t1, t2, t):
    assert len(t1) == len(t2)
    return tuple(
        lerp(i1, i2, t)
        for (i1, i2) in zip(t1, t2)
    )

def lerp(a, b, t):
    if isinstance(a, tuple):
        value = tlerp(a, b, t)
    elif isinstance(a, ppb.Vector):
        value = vlerp(a, b, t)
    elif isinstance(a, int):
        value = ilerp(a, b, t)
    else:
        value = flerp(a, b, t)
    return value


@dataclass
class Tween:
    start_time: float
    end_time: float
    obj: object
    attr: str
    start_value: object
    end_value: object
    easing: str = "linear"


class Tweener:
    """A controller of object transitions over time.
    
    A Tweener has to be added to a scene in order to work! After creating it,
    make multiple calls to tween() to set transitions of object members over
    time. Callbacks may be added to the Tweener with when_done() and all
    callbacks will be invoked when the final transition ends.

    Example:

        t = Tweener()
        t.tween(bomb, 'position', v_target, 1.0)
        t.when_done(play_sound("BOOM"))
    """

    size = 0

    def __init__(self, name=None):
        self.name = name or f"tweener-{id(self)}"
        self.tweens = []
        self.callbacks = []
        # self.used = False
        # self.done = False

    def __hash__(self):
        return hash(id(self))

    @property
    def is_tweening(self):
        return bool(self.tweens)

    def tween(self, entity, attr, end_value, duration, **kwargs):
        assert entity
        delay = kwargs.pop('delay', 0)
        self.used = True
        start_time = monotonic() + delay
        self.tweens.append(Tween(
            start_time=start_time,
            end_time=start_time + duration,
            obj=entity,
            attr=attr,
            start_value=None,
            end_value=end_value,
            **kwargs,
        ))
    
    def when_done(self, func):
        self.callbacks.append(func)

    def on_idle(self, update, signal):
        t = monotonic()
        clear = []

        for i, tween in enumerate(self.tweens):
            if tween.start_time > t:
                continue
            if tween.start_value is None:
                tween.start_value = getattr(tween.obj, tween.attr)
            tr = (t - tween.start_time) / (tween.end_time - tween.start_time)
            tr = min(1.0, max(0.0, tr))
            tr = getattr(easing, tween.easing)(tr)
            value = lerp(tween.start_value, tween.end_value, tr)
            setattr(tween.obj, tween.attr, value)
            if tr >= 1.0:
                clear.append(i)

        for i in reversed(clear):
            del self.tweens[i]
        
        if not self.is_tweening:
            callbacks = self.callbacks[:]
            self.callbacks.clear()
            for func in callbacks:
                func()


class TweenSystem(System):
    scene = None
    current_tweener = None

    @classmethod
    def on_scene_started(cls, ev, signal):
        cls.scene = ev.scene
        cls.current_tweener = Tweener()
        cls.scene.add(cls.current_tweener)
    

def tween(*args, **kwargs):
    TweenSystem.current_tweener.tween(*args, **kwargs)
