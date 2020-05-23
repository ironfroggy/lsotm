from dataclasses import dataclass


@dataclass
class StartGame:
    pass

class RestartGame:
    pass

@dataclass
class OpenMenu:
    pass

@dataclass
class CloseMenu:
    pass

@dataclass
class ToggleMenu:
    pass

@dataclass
class HoverSeed:
    grid: object
    x: int
    y: int

class SeedHeld:
    pass

class SeedReleased:
    pass

@dataclass
class MovementStart:
    colors: dict = None

@dataclass
class MovementDone:
    pass

@dataclass
class TweeningDone:
    tweener: 'systems.tweening.Tweener'

@dataclass
class SeedCorruption:
    x: int
    y: int

@dataclass
class SeedCorruptionComplete:
    pass

@dataclass
class EnemyAttack:
    enemy: object
    dmg: int

@dataclass
class DamageDealt:
    target: str
    dmg: int

@dataclass
class MonsterDeath:
    monster: object

@dataclass
class MonsterSpawn:
    monster: object

@dataclass
class PlayerDeath:
    player: object

@dataclass
class ScorePoints:
    points: int

@dataclass
class ScoreSet:
    points: int

@dataclass
class ScoreUpdated:
    points: int
