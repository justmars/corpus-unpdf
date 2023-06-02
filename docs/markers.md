# Markers

## Metadata

Each document will have:

Page type | Note
--:|:--
_start_ | there will be a deliberate _start_ **y-axis** position affected by _markers_.
_content_ | see [`start-ocr`](https://github.com/justmars/start-ocr) "primitives" `Bodyline` for content segments, `Footnote` for discovered footnote partials.
_end_ | there will be a deliberate _end_ **y-axis** position.

!!! note "Y-axis cutting"

    The **y-axis** is relevant for _start_ and _end_... since the _header_ and the _footer_ are cut out be to arrive at the meat of each page. And each page can then be dissected into segments and footnotes.

!!! Warning

    Not all markers are found in the preliminary page. Hence, need to find anchoring start of content.

## Court Composition

### Composition Choices

::: corpus_unpdf._markers.CourtCompositionChoices

### Extract Composition

::: corpus_unpdf._markers.PositionCourtComposition

## Decision Category & Writer

### Category Choices

::: corpus_unpdf._markers.DecisionCategoryChoices

### Extract Category

::: corpus_unpdf._markers.PositionDecisionCategoryWriter

## Notice

::: corpus_unpdf._markers.PositionNotice
