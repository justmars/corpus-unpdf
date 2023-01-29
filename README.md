# corpus-unpdf

![Github CI](https://github.com/justmars/corpus-unpdf/actions/workflows/main.yml/badge.svg)

Parse Philippine Supreme Court decisions issued in PDF format as text; _hopefully_, this can be utilized in the [LawSQL dataset](https://lawsql.com).

## Documentation

See [documentation](https://justmars.github.io/corpus-unpdf).

## Development

Checkout code, create a new virtual environment:

```sh
poetry add corpus-unpdf # python -m pip install corpus-unpdf
poetry update # install dependencies
poetry shell
```

Run tests:

```sh
pytest
```
