from enum import Enum


class Relation(Enum):
    Child = 1
    Parent = 2
    Associated = 3
    Disassociated = 4
    Needs = 5
    Needed = 6


class Converse(Enum):
    Child = 2
    Needs = 5
