import os
# os.environ["PYSDL2_DLL_PATH"] = os.path.dirname(os.path.abspath(__file__))

import sys, sdl2, sdl2.ext, time
from random import randint
from time import perf_counter

sdl2.ext.init()
window = sdl2.ext.Window("test", size=(800, 600))
window.show()
factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
sprites = [factory.from_image("resources/Spore.png") for i in range(1000)]
for sprite in sprites:
    sprite.position = (randint(0, 800), randint(0, 600))

spriterenderer = factory.create_sprite_render_system(window)
times = []
while len(times) < 10000:
    begin = perf_counter()
    spriterenderer.render(sprites)
    times.append((perf_counter() - begin))
print(1.0 / (sum(times)/len(times)))

window.refresh()