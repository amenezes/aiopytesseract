from dataclasses import dataclass, field


@dataclass(frozen=True)
class Data:
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int
    left: int
    top: int
    width: int
    height: int
    conf: float
    text: str = field(default="")
