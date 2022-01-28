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
async def test_image_to_string_with_path(image):
    text = await aiopytesseract.image_to_string(image)
    assert len(text) > 90


@pytest.mark.asyncio
async def test_image_to_string_with_invalid_type():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.pdf")
