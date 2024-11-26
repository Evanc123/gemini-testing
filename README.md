# Project Setup

## Requirements

- install `uv` https://github.com/astral-sh/uv

## Setup Instructions

## Development

The project uses UV for dependency management. To add new dependencies:

```bash
uv add package_name
```

## Main flow

Run
```bash
uv run main.py
```
to run through the main flow

## Jupyter

Start a jupyter session with

```bash
uv run --with jupyter jupyter lab
```

And select the relevant notebook to run.
