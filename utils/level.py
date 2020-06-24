from dataclasses import dataclass


def load_map(level):
    map_txt = open(f"resources/maps/level{level}.txt").read()
    return map_txt

def parse_map(map_str):
    lines = map_str.strip().split('\n')
    map_width = len(lines[0].split())
    map_height = len(lines)
    rows = map_str.strip().split('\n')
    map = {}
    for i, row in enumerate(rows):
        for j, code in enumerate(row.split()):
            x, y = j - map_width // 2, -i + map_height // 2
            if code == '--':
                cell = None
            else:
                cell = MapCell(x, y, code)
            map[x, y] = cell
    return map

def parse_properties(prop_str):
    properties = {}
    for line in prop_str.split('\n'):
        key, value = line.split('=', 1)
        try:
            value = float(value)
        except ValueError:
            pass
        properties[key] = value
    return properties


@dataclass
class MapCell:
    x: int
    y: int
    code: str


class InvalidKeyError(KeyError):
    pass


class LevelData:
    def __init__(self, level_number):
        self.level_number = level_number
        self.level_str = load_map(level_number)
        self.map_str = self.level_str.split('\n\n', 1)[0]
        self.map_data = parse_map(self.map_str)

        try:
            self.prop_str = self.level_str.split('\n\n', 1)[1]
            self.properties = parse_properties(self.prop_str)
        except IndexError:
            self.prop_str = None
            self.properties = {}
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.properties[key]
        elif isistance(key, tuple):
            return self.map_data[key]
        else:
            raise KeyError("LevelData accepts str and (x, y) keys only.")
    
    def get(self, key, default):
        try:
            return self[key]
        except InvalidKeyError:
            raise
        except KeyError:
            return default


@dataclass
class LevelLoaded:
    number: int
    level: LevelData
