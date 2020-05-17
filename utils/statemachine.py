from dataclasses import dataclass
import typing


@dataclass
class Rule:
    from_state: str
    to_state: str


@dataclass
class StateMachine:
    state: str
    rules: typing.List[Rule]

    def __init__(self, starting, rules):
        self.starting = starting
        self.rules = rules
 