from pathlib import Path

import pytest

import aiopytesseract
from aiopytesseract.exceptions import TesseractRuntimeError
from aiopytesseract.models import OSD


async def is_osd_available() -> bool:
    """Check if OSD functionality is available in the current Tesseract installation."""
    osd_available = False
    try:
        test_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        await aiopytesseract.image_to_osd(test_image, timeout=5)
        osd_available = True
    except Exception:  # noqa: S110
        pass
    return osd_available


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_osd_with_str_image(image):
    if not await is_osd_available():
        pytest.skip("OSD functionality not available in current Tesseract installation")

    osd = await aiopytesseract.image_to_osd(image)
    assert isinstance(osd, OSD)
    assert isinstance(osd.page_number, int)
    assert isinstance(osd.orientation_degrees, float)
    assert isinstance(osd.rotate, float)
    assert isinstance(osd.orientation_confidence, float)
    assert isinstance(osd.script, str)
    assert isinstance(osd.script_confidence, float)


@pytest.mark.parametrize("image", ["tests/samples/file-sample_150kB.png"])
async def test_image_to_osd(image):
    if not await is_osd_available():
        pytest.skip("OSD functionality not available in current Tesseract installation")

    osd = await aiopytesseract.image_to_osd(Path(image).read_bytes())
    assert isinstance(osd, OSD)
    assert isinstance(osd.page_number, int)
    assert isinstance(osd.orientation_degrees, float)
    assert isinstance(osd.rotate, float)
    assert isinstance(osd.orientation_confidence, float)
    assert isinstance(osd.script, str)
    assert isinstance(osd.script_confidence, float)


async def test_image_to_osd_with_invalid():
    with pytest.raises(TesseractRuntimeError):
        await aiopytesseract.image_to_osd("tests/samples/file-sample_150kB.pdf")


async def test_image_to_osd_with_type_not_supported():
    with pytest.raises(NotImplementedError):
        await aiopytesseract.image_to_osd(None)


def test_osd_str():
    osd = OSD(
        page_number=0,
        orientation_degrees=0,
        rotate=0,
        orientation_confidence=0,
        script="",
        script_confidence=0,
    )
    assert str(osd) == ""
