from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.parameter import Parameter


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


# run
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
async def test_confidence():
    confidence = await aiopytesseract.confidence("tests/samples/file-sample_150kB.png")
    assert confidence == "2.00"


@pytest.mark.asyncio
async def test_confidence_without_result():
    confidence = await aiopytesseract.confidence("tests/samples/file-sample_150kB.pdf")
    assert confidence is None


@pytest.mark.asyncio
async def test_deskew():
    deskew = await aiopytesseract.deskew("tests/samples/file-sample_150kB.png")
    assert deskew == "0.0000"


@pytest.mark.asyncio
async def test_deskew_without_result():
    deskew = await aiopytesseract.deskew("tests/samples/file-sample_150kB.pdf")
    assert deskew is None


@pytest.mark.asyncio
async def test_tesseract_parameters():
    parameters = await aiopytesseract.tesseract_parameters()
    assert isinstance(parameters, list)
    assert isinstance(parameters[0], Parameter)
