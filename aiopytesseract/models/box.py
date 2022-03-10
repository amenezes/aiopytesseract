from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    character: str
    x: int
    y: int
    w: int
    h: int
