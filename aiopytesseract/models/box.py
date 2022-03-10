from dataclasses import dataclass


@dataclass
class Box:
    character: str
    x: int
    y: int
    w: int
    h: int
