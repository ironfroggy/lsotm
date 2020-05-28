import ctypes
import io
import logging
import random
from time import monotonic

from sdl2 import (
    SDL_BLENDMODE_ADD,
    SDL_BLENDMODE_BLEND,
    SDL_FLIP_NONE,
    SDL_FLIP_HORIZONTAL,
    SDL_FLIP_VERTICAL,
    SDL_RenderCopyEx,
    SDL_RenderPresent,
    SDL_SetTextureAlphaMod,
    SDL_SetTextureBlendMode,
    SDL_SetTextureColorMod,
    SDL_QueryTexture,
    SDL_Rect,
)
import sdl2
import sdl2.ext

import ppb.flags as flags
from ppb.systems._sdl_utils import sdl_call
from ppb.systems import Renderer


class CustomRenderer(Renderer):

    def on_render(self, render_event, signal):
        camera = render_event.scene.main_camera

        self.render_background(render_event.scene)

        for game_object in render_event.scene.sprite_layers():
            texture = self.prepare_resource(game_object)
            if texture is None:
                continue
            src_rect, dest_rect, angle = self.compute_rectangles(
                texture.inner, game_object, camera
            )
            flip = getattr(game_object, 'flip', SDL_FLIP_NONE)
            sdl_call(
                SDL_RenderCopyEx, self.renderer, texture.inner,
                ctypes.byref(src_rect), ctypes.byref(dest_rect),
                angle, None, flip,
                _check_error=lambda rv: rv < 0
            )
        sdl_call(SDL_RenderPresent, self.renderer)
    
    def compute_rectangles(self, texture, game_object, camera):
        flags = sdl2.stdinc.Uint32()
        access = ctypes.c_int()
        img_w = ctypes.c_int()
        img_h = ctypes.c_int()
        sdl_call(
            SDL_QueryTexture, texture, ctypes.byref(flags), ctypes.byref(access),
            ctypes.byref(img_w), ctypes.byref(img_h),
            _check_error=lambda rv: rv < 0
        )

        rect = getattr(game_object, 'rect', None)
        if rect:
            src_rect = SDL_Rect(*rect)
            win_w = rect[2] * game_object.size
            win_h = rect[3] * game_object.size
        else:
            src_rect = SDL_Rect(x=0, y=0, w=img_w, h=img_h)
            if hasattr(game_object, 'width'):
                obj_w = game_object.width
                obj_h = game_object.height
            else:
                obj_w, obj_h = game_object.size

            win_w, win_h = self.target_resolution(img_w.value, img_h.value, obj_w, obj_h, camera.pixel_ratio)

        center = camera.translate_point_to_screen(game_object.position)
        dest_rect = SDL_Rect(
            x=int(center.x - win_w / 2),
            y=int(center.y - win_h / 2),
            w=int(win_w),
            h=int(win_h),
        )

        return src_rect, dest_rect, ctypes.c_double(-game_object.rotation)