from enum import Enum


class Relation(Enum):
    Child = 1
    Parent = 2
    Associated = 3
    Disassociated = 5


class Converse(Enum):
    Child = 1
    Parent = 2
