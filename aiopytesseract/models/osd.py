from attrs import frozen


@frozen
class OSD:
    page_number: int
    orientation_degrees: float
    rotate: float
    orientation_confidence: float
    script: str
    script_confidence: float

    def __str__(self) -> str:
        return self.script
