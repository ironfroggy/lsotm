from constants import *

MIN_Y = -8
MAX_Y = 8

Y_WIDTH = MAX_Y - MIN_Y
LAYER_DEPTH = LAYER_GAMEPLAY_HIGH - LAYER_GAMEPLAY_LOW

def pos_to_layer(position):
    layer = -position.y
    layer = min(layer, MAX_Y)
    layer = max(layer, MIN_Y)
    return LAYER_GAMEPLAY_LOW + ((layer - MIN_Y) / Y_WIDTH) * LAYER_DEPTH
