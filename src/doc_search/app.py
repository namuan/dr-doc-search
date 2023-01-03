"""
Indexes a PDF file and generate OpenAI Embeddings
"""
import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path

from doc_search import setup_logging


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        "-i", "--input", required=True, type=Path, help="Path to input file"
    )
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
    logging.info("Do something")


if __name__ == "__main__":  # pragma: no cover
    main()
