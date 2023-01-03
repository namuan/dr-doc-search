# Doc Search

[![PyPI](https://img.shields.io/pypi/v/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)
[![PyPI - License](https://img.shields.io/pypi/l/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)


---

**Documentation**: [https://namuan.github.io/dr-doc-search](https://namuan.github.io/dr-doc-search)

**Source Code**: [https://github.com/namuan/dr-doc-search](https://github.com/namuan/dr-doc-search)

**PyPI**: [https://pypi.org/project/dr-doc-search/](https://pypi.org/project/dr-doc-search/)

---

Search through a document using a chat interface.

## Installation

```sh
pip install dr-doc-search
```

## Example Usage

```shell
dr-doc-search --help
```

## Development

* Clone this repository
* Requirements:
  * Python 3.7+
  * [Poetry](https://python-poetry.org/)
  * [Comby](https://comby.dev/docs/)

* Create a virtual environment and install the dependencies
```sh
poetry install
```

* Activate the virtual environment
```sh
poetry shell
```

### Validating build
```sh
make build
```

### Release process
A release is automatically published when a new version is bumped using `make bump`.
See `.github/workflows/build.yml` for more details.
Once the release is published, `.github/workflows/publish.yml` will automatically publish it to PyPI.
