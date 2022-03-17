import pytest

from aiopytesseract.file_format import FileFormat


@pytest.mark.parametrize("output_format", ["alto", "hocr", "pdf", "tsv", "txt"])
async def test_tesseract_formats_supported(output_format):
    assert output_format in list(FileFormat)


@pytest.mark.parametrize(
    "output_format, fileformat",
    [
        ("alto", FileFormat.ALTO),
        ("hocr", FileFormat.HOCR),
        ("pdf", FileFormat.PDF),
        ("tsv", FileFormat.TSV),
        ("txt", FileFormat.TXT),
    ],
)
async def test_file_format_str(output_format, fileformat):
    assert output_format == fileformat
