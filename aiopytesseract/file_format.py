from enum import Enum, unique


@unique
class FileFormat(str, Enum):
    ALTO: str = "alto"
    HOCR: str = "hocr"
    PDF: str = "pdf"
    TSV: str = "tsv"
    TXT: str = "txt"
    OSD: str = "osd"

    def __str__(self) -> str:
        return str.__str__(self)
