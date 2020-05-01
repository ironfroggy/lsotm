import ppb
from ppb.systems.sound import SoundController


class Player(ppb.BaseSprite):
    pass


class MainScene(ppb.BaseScene):

    # Annotate the scene with requested systems to interact with
    sound: SoundController

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(Player())

    def on_scene_started(self, ev, signal):

        # Interact with a system
        print(self.sound.allocated_channels)


ppb.run(starting_scene=MainScene)