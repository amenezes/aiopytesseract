from dataclasses import dataclass


@dataclass
class OSD:
    page_number: int
    orientation_degrees: float
    rotate: float
    orientation_confidence: float
    script: str
    script_confidence: float
