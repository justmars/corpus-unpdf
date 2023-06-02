# corpus-unpdf Docs

Utilizes [`start-ocr`](https://github.com/justmars/start-ocr) "primitive" functions.

## Applicability

Documents in PH Supreme Court 2023 website:

1. Decision / Resolution
2. Separate Opinions in the latter

Each document will have:

Page type | Note
--:|:--
_start_ | there will be a deliberate _start_ "y-axis" position affected by _markers_
_content_ | see `start-ocr`
_end_ | there will be a deliberate _end_ "y-axis" position

The y-axis is relevant to slice the _header_ and the _footer_ to arrive at the meat of each page.

## get_decision

:::corpus_unpdf.decision.get_decision

## DecisionMeta

:::corpus_unpdf.decision.DecisionMeta

## get_opinion

:::corpus_unpdf.decision.get_opinion
