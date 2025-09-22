from attrs import field, frozen


@frozen
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
    text: str = field(factory=str)

    def __str__(self) -> str:
        return self.text
