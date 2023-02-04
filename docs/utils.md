# Utils

## Fetch PDFs

Work with pdf files.

### Extract page, image

:::corpus_unpdf.src.common.fetch.get_page_and_img

### Reverse list pages, images

:::corpus_unpdf.src.common.fetch.get_reverse_pages_and_imgs

### Get terminal page, position

:::corpus_unpdf.src.common.fetch.get_terminal_page_pos

## Slice images & pages

Using pre-processed PDF files above, slice images and/or pages based on certain
criteria.

### Get contours from image

:::corpus_unpdf.src.common.slice.get_contours

### Test image matches text

:::corpus_unpdf.src.common.slice.is_match_text

### Centered text matching contours

:::corpus_unpdf.src.common.slice.get_centered_coordinates

### Get slice of page

:::corpus_unpdf.src.common.slice.PageCut
