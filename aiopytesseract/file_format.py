from enum import Enum, unique


@unique
class FileFormat(str, Enum):
    ALTO = "alto"
    HOCR = "hocr"
    PDF = "pdf"
    TSV = "tsv"
    TXT = "txt"
    OSD = "osd"

    def __str__(self) -> str:
        return str.__str__(self)
