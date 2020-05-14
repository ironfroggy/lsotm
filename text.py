import ppb


FONTSHEET = ppb.Image("resources/font2.png")
# LEGEND = """ !"#$%&'
# <>*+,-./
# 01234567
# 89:;<=>?
# @ABCDEFG
# HIJKLMNO
# PQRSTUVW
# XYZ[\]^_
# `abcdefg
# hijklmno
# pqrstuvw
# xyz{|}~
# """

LEGEND = """
                

 !"#$%&'()*+,-./
0123456789:;<=>?
@ABCDEFGHIJKLMNO
PQRSTUVWXYZ[\]^_
`abcdefghijklmno
pqrstuvwxyz{|}~ 
"""[1:]

class Letter(ppb.Sprite):
    image = FONTSHEET
    rect = (0, 0, 16, 16)
    size = 2.0

    def __init__(self, char, color):
        super().__init__()
        self.char = char
        self.color = color
        for y, row in enumerate(LEGEND.split('\n')):
            for x, col in enumerate(row):
                if char in col:
                    self.rect = (x*16, y*16, 16, 16)
                    return

class Text:
    def __init__(self, text, position, layer=100, align='center', color=(255, 255, 255)):
        self._position = position
        self.layer = layer
        self.align = align
        self.signal = None
        self.letters = []
        self._text = text
        self._size = 2.0
        self._color = color
        self._opacity = 255
    
    def __image__(self):
        return None

    def on_scene_started(self, ev, signal):
        self.scene = ev.scene
        self.text = self._text
    
    def setup(self):
        self.text = self._text
    
    @property
    def text(self):
        return self._text
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
        for l in self.letters:
            l.size = value
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
        for l in self.letters:
            l.color = value

    @property
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        for l in self.letters:
            l.opacity = value

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        d = self._position - value
        self._position = value
        for l in self.letters:
            l.position += d

    @text.setter
    def text(self, value):
        self._text = value
        for l in self.letters:
            self.scene.remove(l)
        self.letters.clear()
        
        p = self.position

        if self.align == 'center':
            align = -0.25 * len(self.text)
        elif self.align == 'left':
            raise NotImplementedError()
        elif self.align == 'right':
            align = 0
        else:
            raise ValueError()

        for i, c in enumerate(self.text):
            l = Letter(c, self._color)
            l.layer = self.layer
            l.position = ppb.Vector(p.x + i/2 + align, p.y)
            self.scene.add(l)
            self.letters.append(l)
