MIN_Y = -8
MAX_Y = 8
MIN_LAYER = 100
MAX_LAYER = 199

Y_WIDTH = MAX_Y - MIN_Y
LAYER_DEPTH = MAX_LAYER - MIN_LAYER

def pos_to_layer(position):
    layer = -position.y
    layer = min(layer, MAX_Y)
    layer = max(layer, MIN_Y)
    return MIN_LAYER + ((layer - MIN_Y) / Y_WIDTH) * LAYER_DEPTH
