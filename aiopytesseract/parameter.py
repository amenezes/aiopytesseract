from dataclasses import dataclass


@dataclass
class Parameter:
    name: str
    value: str
    description: str
