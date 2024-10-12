# Markdown PyCon

[![ci](https://github.com/pawamoy/markdown-pycon/workflows/ci/badge.svg)](https://github.com/pawamoy/markdown-pycon/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://pawamoy.github.io/markdown-pycon/)
[![pypi version](https://img.shields.io/pypi/v/markdown-pycon.svg)](https://pypi.org/project/markdown-pycon/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-708FCC.svg?style=flat)](https://gitpod.io/#https://github.com/pawamoy/markdown-pycon)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#markdown-pycon:gitter.im)

Markdown extension to parse `pycon` code blocks without indentation or fences.

## Installation

```bash
pip install markdown-pycon
```

## Configuration

This extension relies on the
[Highlight](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/)
extension of
[PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/).

Configure from Python:

```python
from markdown import Markdown

Markdown(extensions=["pycon"])
```

...or in MkDocs configuration file, as a Markdown extension:

```yaml
# mkdocs.yml
markdown_extensions:
- pycon
```

## Usage

In your Markdown documents, simply write your `pycon` code blocks
without indentation or fences (triple backticks):

```md
>>> print("This is a pycon code block")
This is a pycon code block
```

This will get rendered as:

```pycon
>>> print("This is a pycon code block")
This is a pycon code block
```

[Doctest flags](https://docs.python.org/3/library/doctest.html#option-flags)
will be removed from the code lines.
