from pathlib import Path

import pytest

import aiopytesseract


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_boxes_with_str_image(image):
    boxes = await aiopytesseract.image_to_boxes(image)
    assert isinstance(boxes, str)
    assert len(boxes) == 1405


@pytest.mark.asyncio
@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_boxes_with_bytes_image(image):
    boxes = await aiopytesseract.image_to_boxes(Path(image).read_bytes())
    assert isinstance(boxes, str)
    assert len(boxes) == 1405


@pytest.mark.asyncio
async def test_image_to_boxes_with_invalid():
    with pytest.raises(RuntimeError):
        await aiopytesseract.image_to_boxes("tests/samples/file-sample_150kB.pdf")


@pytest.mark.asyncio
async def test_image_to_boxes_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_boxes(None)
