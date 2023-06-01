# corpus-unpdf Docs

Requires `start-ocr`.

## Flow

1. As a document:
      1. Determine _start_ page and _start_ "y-axis" position coordinate as [start elements][start-of-content], note that is greatly affected by [markers][markers]
      2. Determine _end_ page and _start_ "y-axis" position coordinate as [end elements][end-of-content]
2. For _each page_:
      1. Determine "y-axis" to slice [header][header-of-page]
      2. Determine "y-axis" to slice [footer][footer-of-page]

!!! Note

    For slicing to work, each pdf's page, opened and cropped via `pdfplumber`, must be converted an to an `opencv` image format (i.e. `numpy.ndarray`). This enables discovery of [contours][get-contours-from-image] that can act as borders for slicing content from the page.
