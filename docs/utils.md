# Utils

## Fetch PDFs

Work with pdf files.

### Extract page, image

:::corpus_unpdf.src.common.fetch.get_page_and_img

### Reverse list pages, images

:::corpus_unpdf.src.common.fetch.get_reverse_pages_and_imgs

## Slice images & pages

Using pre-processed PDF files above, slice images and/or pages based on certain
criteria.

### Get contours from image

:::corpus_unpdf.src.common.slice.get_contours

### Centered text matching contours

:::corpus_unpdf.src.common.slice.get_centered_coordinates

### Get slice of page

Note the two kinds of measurements involved.

A `page`  is based on `pdfplumber`'s points.

An `image` is based on pixels.

In order to use the image's pixels as page points, use the
the image's max width / height as the divisor to get the ratio
and then apply that ratio (percentage) to the page's max width / height.
See related [answer](https://stackoverflow.com/a/73404598)

:::corpus_unpdf.src.common.slice.PageCut
