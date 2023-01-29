# Doc Search

[![PyPI](https://img.shields.io/pypi/v/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)
[![PyPI - License](https://img.shields.io/pypi/l/dr-doc-search?style=flat-square)](https://pypi.python.org/pypi/dr-doc-search/)

Converse with a book (PDF)

![](assets/dr-doc-search-github-demo.gif)

See [tweet](https://twitter.com/deskriders_twt/status/1612088387984588802) for full demo.

---

**Documentation**: [https://namuan.github.io/dr-doc-search](https://namuan.github.io/dr-doc-search)

**Source Code**: [https://github.com/namuan/dr-doc-search](https://github.com/namuan/dr-doc-search)

**PyPI**: [https://pypi.org/project/dr-doc-search/](https://pypi.org/project/dr-doc-search/)

---

## Pre-requisites

- [Tessaract OCR](https://github.com/tesseract-ocr/tesseract)
- [ImageMagick](https://imagemagick.org/index.php)

## Installation

```sh
pip install dr-doc-search
```

## Example Usage

There are two steps to use this application:

**1.** First, you need to create the index and generate embeddings for the PDF file.
Here I'm using a PDF file generated from this page [Parable of a Monetary Economy
   ](http://heteconomist.com/parable-of-a-monetary-economy/)

Before running this, you need to set up your OpenAI API key. You can get it from [OpenAI](https://beta.openai.com/account/api-keys).

> From version 1.5.0, you can skip OpenAI and use HuggingFace models to generate embeddings and answers.

```shell
export OPENAI_API_KEY=<your-openai-api-key>
```

The run the following command to start the training process:

```shell
dr-doc-search --train -i ~/Downloads/parable-of-a-monetary-economy-heteconomist.pdf
```

Use `huggingface` for generating embeddings:

```shell
dr-doc-search --train -i ~/Downloads/parable-of-a-monetary-economy-heteconomist.pdf --embedding huggingface
```

The training process generates some temporary files in the `OutputDir/dr-doc-search/<pdf-name>` folder under your home directory.
Here is what it looks like:

```text
 ~/OutputDir/dr-doc-search/parable-of-a-monetary-economy-heteconomist
$ tree
.
├── images
│ ├── output-1.png
│ ├── output-10.png
│ ├── output-11.png
...
│ └── output-9.png
├── index
│ ├── docsearch.index
│ └── index.pkl
├── parable-of-a-monetary-economy-heteconomist.pdf
└── scanned
    ├── output-1.txt
    ...
    └── output-9.txt
```

> **Note:**
> It is possible to change the base of the output directory by providing the `--app-dir` argument.

**2.** Now that we have the index, we can use it to start asking questions.

```shell
dr-doc-search -i ~/Downloads/parable-of-a-monetary-economy-heteconomist.pdf --input-question "How did the attempt to reduce the debut resulted in decrease in employment?"
```

Or You can open up a web interface (on port :5006) to ask questions:

```shell
dr-doc-search --web-app -i ~/Downloads/parable-of-a-monetary-economy-heteconomist.pdf
```

To use `huggingface` model, provide the `--llm` argument:

```shell
dr-doc-search --web-app -i ~/Downloads/parable-of-a-monetary-economy-heteconomist.pdf --llm huggingface
```

There are more options for choose the start and end pages for the PDF file.
See the help for more details:

```shell
dr-doc-search --help
```

## Acknowledgements

- [anton/@abacaj](https://twitter.com/abacaj/status/1608163940726358024) for the idea
- [LangChain](https://github.com/hwchase17/langchain)
- [HoloViz Panel](https://panel.holoviz.org/)
- [OpenAI](https://beta.openai.com/)

## Development

* Clone this repository
* Requirements:
  * Python 3.7+
  * [Poetry](https://python-poetry.org/)

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

### Disclaimer

This project is not affiliated with OpenAI.
The OpenAI API and GPT-3 language model are not free after the trial period.
