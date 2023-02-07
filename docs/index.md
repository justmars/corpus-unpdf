# corpus-unpdf Docs

PDF, as a file format, is the bane of programmatic text analysis.

It's not a document format like `.txt`, `.docx`, `.md`, etc. where elements of a document such as (a) layout, (b) words, (c) lines, etc. can be extracted easily.

Instead, PDFs can be equated to instructions producing human-_comprehensible_, yet machine-_confusing_ outputs.

Humans can eyeball these outputs and understand the result. Machines however can only parse and make a guess as to its contents. Put another way:

!!! Note

    PDF = humans good, machines bad

In light of this context, this library is an attempt to parse Philippine Supreme Court decisions issued in PDF format and extract its raw "as guessed" output.

## Flow

1. As a document:
      1. Determine _start_ page and _start_ "y-axis" position coordinate as [start elements][start-of-content], note that is greatly affected by [markers][markers]
      2. Determine _end_ page and _start_ "y-axis" position coordinate as [end elements][end-of-content]
2. For _each page_:
      1. Determine "y-axis" to slice [header][header-of-page]
      2. Determine "y-axis" to slice [footer][footer-of-page]

!!! Note

    For slicing to work, each pdf's page, opened and cropped via `pdfplumber`, must be converted an to an `opencv` image format (i.e. `numpy.ndarray`). This enables discovery of [contours][get-contours-from-image] that can act as borders for slicing content from the page.

## Measurements

Since we'll be using two distinct libraries with different formats, pay attention to the kind of measurements involved.

### Unit

Library | Unit | Description | Maximum
--:|:--|:--|:--:
_pdfplumber_ | point | PDF unit | `im.shape` gets a tuple of the image dimensions
_opencv_ | pixel | Graphical unit | `page.height * page.width` is the size of the page

!!! Warning

    Convert image's pixels as page points, by first getting image ratio; then apply ratio (percentage)
    to the page's max width / height.

    ```py
    >>> from corpus_unpdf.src.common import get_contours # shortcut custom function
    >>> im_h, im_w, im_d = im.shape # im_h is maximum image height
    >>> test = next(cv2.boundingRect(c) for c in get_contours(im, (50, 10)))
    >>> x, y, w, h = test # see Slicing below
    >>> ratio = y / im_h # `y` coordinate over `im_h` gives a pixel-based ratio
    >>> page_point = ratio * page.height # equivalent point in PDF page
    ```

    See related [discussion](https://stackoverflow.com/a/73404598).

### Boxes

#### Slicing opencv

!!! Note "Rectangles for opencv"
    Reference | Expectation | Format | Unit
    :--:|:--:|:--:|:--:
    _cv2.boundingRect()_ | Results in a tuple of four points | (`x`,`y`,`w`,`h`) | pixels

Fields | Meaning
--:|:--
`x` | point in x-axis
`y` | point in y-axis
`w` | width
`h` | height

#### Slicing pdfplumber

!!! Note "Rectangles for pdfplumber"
    Reference | Expectation | Format | Unit
    :--:|:--:|:--:|:--:
    _pdfplumber._typing.T_bbox_ | A tuple of four points | (`x0`, `y0`, `x1`, `y1`) | points

Fields | Meaning
--:|:--
`x0` | left-most point in _x-axis_
`x1` | right-most point in _x-axis_
`y0` | top-most point in _y-axis_
`y1` | bottom-most point in _y-axis_

## Setup

### Common libraries

Install common libraries in MacOS with `homebrew`:

```sh
brew install tesseract
brew install imagemagick
brew info imagemagick # check version
```

The last command gets you the local folder installed which will be needed in creating the virtual environment:

```sh
==> imagemagick: stable 7.1.0-61 (bottled), HEAD # note the version number
Tools and libraries to manipulate images in many formats
https://imagemagick.org/index.php
/opt/homebrew/Cellar/imagemagick/7.1.0-61 (807 files, 31MB) * # first part is the local folder
x x x
```

Note that both `tesseract` and `imagemagick` libraries are also made preconditions in `.github/workflows/main.yaml`:

```yaml
steps:
  # see https://github.com/madmaze/pytesseract/blob/master/.github/workflows/ci.yaml
  - name: Install tesseract
    run: sudo apt-get -y update && sudo apt-get install -y tesseract-ocr tesseract-ocr-fra
  - name: Print tesseract version
    run: echo $(tesseract --version)

  # see https://github.com/jsvine/pdfplumber/blob/stable/.github/workflows/tests.yml
  - name: Install ghostscript & imagemagick
    run: sudo apt update && sudo apt install ghostscript libmagickwand-dev
  - name: Remove policy.xml
    run: sudo rm /etc/ImageMagick-6/policy.xml # this needs to be removed or the test won't run
```

### Virtual environment

!!! warning "Update `.env` whenever `imagemagick` changes"

    The shared dependency is based on `MAGICK_HOME` folder. This can't seem to be
    fetched by python (at least in 3.11) so we need to help it along by explicitly
    declaring its location. The folder can change when a new version is installed
    via `brew upgrade imagemagick`

Create an .env file and use the folder as the environment variable `MAGICK_HOME`:

```.env
MAGICK_HOME=/opt/homebrew/Cellar/imagemagick/7.1.0-61
```

This configuration will allow `pdfplumber` to detect `imagemagick`.

Effect of not setting `MAGICK_HOME`:

```py
>>> import pdfplumber
>>> pdfplumber.open<(testpath>).pages[0].to_image(resolution=300) # ERROR
```

```text
OSError: cannot find library; tried paths: []

During handling of the above exception, another exception occurred:

ImportError                               Traceback (most recent call last)
...
ImportError: MagickWand shared library not found.
You probably had not installed ImageMagick library.
Try to install:
  brew install freetype imagemagick
```

With `MAGICK_HOME`:

```py
>>> import pdfplumber
>>> pdfplumber.open<(testpath>).pages[0].to_image
PIL.Image.Image # image library and type detected
```

Proceed to create the environment using `poetry update` which will install the following into a separate virtual environment:

```toml
[tool.poetry.dependencies]
python = "^3.11"
python-dotenv = "^0.21"
pdfplumber = "^0.7.6" # from pdf to txt
pillow = "^9.4.0" # from pdf to img
opencv-python = "^4.7.0.68" # img manipulation
pytesseract = "^0.3.10" # map manipulated img
```
