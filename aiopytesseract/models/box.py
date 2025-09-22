from attrs import frozen


@frozen
class Box:
    character: str
    x: int
    y: int
    w: int
    h: int

    def __str__(self) -> str:
        return self.character
