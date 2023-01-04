"""
Indexes a PDF file and generate OpenAI Embeddings
"""
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path

from py_executable_checklist.workflow import run_workflow

from doc_search import setup_logging
from doc_search.workflow import workflow_steps


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input-pdf-path", required=True, type=Path, help="Path to input PDF file")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbose",
        help="Increase verbosity of logging output",
    )
    return parser.parse_args()


def main() -> None:  # pragma: no cover
    args = parse_args()
    setup_logging(args.verbose)
    context = args.__dict__
    run_workflow(context, workflow_steps())


if __name__ == "__main__":  # pragma: no cover
    main()
