from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractTimeoutError, TesseractRuntimeError
from aiopytesseract.models import Parameter


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func", [aiopytesseract.languages, aiopytesseract.get_languages]
)
async def test_languages(func):
    languages = await func()
    assert isinstance(languages, list)
    assert len(languages) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func", [aiopytesseract.tesseract_version, aiopytesseract.get_tesseract_version]
)
async def test_tesseract_version(func):
    version = await func()
    assert isinstance(version, str)
    assert len(version) > 0


@pytest.mark.asyncio
async def test_run_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        async with aiopytesseract.run(
            "tests/samples/file-sample_150kB.png", "demo", "alto tsv"
        ) as output:
            print(output)


@pytest.mark.asyncio
async def test_run_with_bytes_image():
    async with aiopytesseract.run(
        Path("tests/samples/file-sample_150kB.png").read_bytes(),
        "output",
        "txt tsv pdf",
    ) as resp:
        txt_file, tsv_file, pdf_file = resp
        assert len(resp) == 3
        assert Path(txt_file).exists()
        assert Path(tsv_file).exists()
        assert Path(pdf_file).exists()
    assert not Path(txt_file).exists()
    assert not Path(tsv_file).exists()
    assert not Path(pdf_file).exists()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "image_file, expected",
    [
        ("tests/samples/file-sample_150kB.png", 2.0),
        ("tests/samples/file-sample_150kB.pdf", 0.0),
    ],
)
async def test_confidence(image_file, expected):
    confidence = await aiopytesseract.confidence(image_file)
    assert confidence == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "image_file, expected",
    [
        ("tests/samples/file-sample_150kB.png", 0.0),
        ("tests/samples/file-sample_150kB.pdf", 0.0),
    ],
)
async def test_deskew(image_file, expected):
    deskew = await aiopytesseract.deskew(image_file)
    assert deskew == expected


@pytest.mark.asyncio
async def test_tesseract_parameters():
    parameters = await aiopytesseract.tesseract_parameters()
    assert isinstance(parameters, list)
    assert isinstance(parameters[0], Parameter)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func, timeout",
    [
        (aiopytesseract.image_to_string, 0.1),
        (aiopytesseract.image_to_hocr, 0.1),
        (aiopytesseract.image_to_osd, 0.1),
        (aiopytesseract.image_to_pdf, 0.1),
        (aiopytesseract.image_to_data, 0.1),
        (aiopytesseract.image_to_boxes, 0.1),
        (aiopytesseract.deskew, 0.01),
        (aiopytesseract.confidence, 0.1),
    ],
)
async def test_method_timeout(func, timeout):
    with pytest.raises(TesseractTimeoutError):
        await func("tests/samples/file-sample_150kB.png", timeout=timeout)


async def test_run_timeout():
    with pytest.raises(TesseractRuntimeError):
        async with aiopytesseract.run(
            Path("tests/samples/file-sample_150kB.png").read_bytes(),
            "xxx",
            "alto tsv txt",
            timeout=0.1,
        ) as out:
            print(out)
