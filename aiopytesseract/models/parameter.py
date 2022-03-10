from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    name: str
    value: float
    description: str
