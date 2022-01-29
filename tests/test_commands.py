from pathlib import Path

import pytest

import aiopytesseract


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func", [aiopytesseract.languages, aiopytesseract.get_languages]
)
async def test_languages(func):
    languages = await func()
    assert len(languages) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func", [aiopytesseract.tesseract_version, aiopytesseract.get_tesseract_version]
)
async def test_tesseract_version(func):
    version = await func()
    assert isinstance(version, str)


@pytest.mark.asyncio
async def test_image_to_string_with_any():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_string(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_str_image(image):
    text = await aiopytesseract.image_to_string(image)
    assert len(text) > 90


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_string_with_bytes_image(image):
    text = await aiopytesseract.image_to_string(Path(image).read_bytes())
    assert len(text) > 90


@pytest.mark.asyncio
async def test_image_to_string_with_invalid():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_run_with_str_image():
    async with aiopytesseract.run(
        "tests/samples/file-sample_150kB.png", "output", "txt tsv pdf"
    ) as resp:
        txt_file, tsv_file, pdf_file = resp
        assert len(resp) == 3
        assert Path(txt_file).exists()
        assert Path(tsv_file).exists()
        assert Path(pdf_file).exists()


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
