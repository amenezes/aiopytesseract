[![ci](https://github.com/amenezes/aiopytesseract/actions/workflows/ci.yml/badge.svg)](https://github.com/amenezes/aiopytesseract/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/amenezes/aiopytesseract/branch/master/graph/badge.svg)](https://codecov.io/gh/amenezes/aiopytesseract)
[![PyPI version](https://badge.fury.io/py/aiopytesseract.svg)](https://badge.fury.io/py/aiopytesseract)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiopytesseract)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# aiopytesseract

A Python [asyncio](https://docs.python.org/3/library/asyncio.html) wrapper for [Tesseract-OCR](https://tesseract-ocr.github.io/tessdoc/).

## Installation

Install and update using pip:

````bash
pip install aiopytesseract
````

## Usage

### List all available languages by Tesseract installation

``` python
import aiopytesseract

await aiopytesseract.languages()
await aiopytesseract.get_languages()
```

### Tesseract version

``` python
import aiopytesseract

await aiopytesseract.tesseract_version()
await aiopytesseract.get_tesseract_version()
```

### Tesseract parameters

``` python
import aiopytesseract

await aiopytesseract.tesseract_parameters()
```

### Confidence only info

``` python
import aiopytesseract

await aiopytesseract.confidence("tests/samples/file-sample_150kB.png")
```

### Deskew info

``` python
import aiopytesseract

await aiopytesseract.deskew("tests/samples/file-sample_150kB.png")
```

### Extract text from an image: locally or bytes

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_string("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_string(
	Path("tests/samples/file-sample_150kB.png").read_bytes(), dpi=220, lang='eng+por'
)
```

### Box estimates

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_boxes("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_boxes(Path("tests/samples/file-sample_150kB.png")
```

### Boxes, confidence and page numbers

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_data("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_data(Path("tests/samples/file-sample_150kB.png")
```

### Information about orientation and script detection

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_osd("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_osd(Path("tests/samples/file-sample_150kB.png")
```

### Generate a searchable PDF

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_pdf("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_pdf(Path("tests/samples/file-sample_150kB.png")
```

### Generate HOCR output

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_hocr("tests/samples/file-sample_150kB.png")
await aiopytesseract.image_to_hocr(Path("tests/samples/file-sample_150kB.png")
```

### Multi ouput

``` python
from pathlib import Path

import aiopytesseract

async with aiopytesseract.run(
	Path('tests/samples/file-sample_150kB.png').read_bytes(),
	'output',
	'alto tsv txt'
) as resp:
	# will generate (output.xml, output.tsv and output.txt)
	print(resp)
	alto_file, tsv_file, txt_file = resp
```

### Config variables

``` python
from pathlib import Path

import aiopytesseract

async with aiopytesseract.run(
	Path('tests/samples/text-with-chars-and-numbers.png').read_bytes(),
	'output',
	'alto tsv txt'
	config=[("tessedit_char_whitelist", "0123456789")]
) as resp:
	# will generate (output.xml, output.tsv and output.txt)
	print(resp)
	alto_file, tsv_file, txt_file = resp
```

``` python
from pathlib import Path

import aiopytesseract

await aiopytesseract.image_to_string(
	"tests/samples/text-with-chars-and-numbers.png",
	config=[("tessedit_char_whitelist", "0123456789")]
)

await aiopytesseract.image_to_string(
	Path("tests/samples/text-with-chars-and-numbers.png").read_bytes(),
	dpi=220,
	lang='eng+por',
	config=[("tessedit_char_whitelist", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")]
)
```

> For more details on Tesseract best practices and the aiopytesseract, see the folder: `docs`.

## Examples

If you want to test **aiopytesseract** easily, can you use some options like:

- docker/docker-compose
- [streamlit](https://streamlit.io)

### Docker / docker-compose

After clone this repo run the command below:

```bash
docker-compose up -d
```

### streamlit app

For this option it's necessary first install `aiopytesseract` and `streamlit`, after execute:

``` py
# remote option:
streamlit run https://github.com/amenezes/aiopytesseract/blob/master/examples/streamlit/app.py
```

``` py
# local option:
streamlit run examples/streamlit/app.py
```

> note: The streamlit example need **python >= 3.10**

## Links

- License: [Apache License](https://choosealicense.com/licenses/apache-2.0/)
- Code: [https://github.com/amenezes/aiopytesseract](https://github.com/amenezes/aiopytesseract)
- Issue tracker: [https://github.com/amenezes/aiopytesseract/issues](https://github.com/amenezes/aiopytesseract/issues)
- Docs: [https://github.com/amenezes/aiopytesseract](https://github.com/amenezes/aiopytesseract)
