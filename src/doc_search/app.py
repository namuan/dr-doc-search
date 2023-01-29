"""
Indexes a PDF file and generate OpenAI Embeddings.
Also allow user to ask question using the command line interface or the web app.
"""
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path

from py_executable_checklist.workflow import run_workflow
from rich import print

from doc_search import setup_logging
from doc_search.web import run_web
from doc_search.workflow import (
    pre_process_workflow_steps,
    training_workflow_steps,
    workflow_steps,
)


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input-pdf-path", required=True, type=Path, help="Path to input PDF file")
    parser.add_argument("-d", "--app_dir", default=Path.home(), type=Path, help="Path to app directory")
    parser.add_argument(
        "-s", "--start-page", default=-1, type=int, help="Specify if you want to start from a specific page"
    )
    parser.add_argument("-e", "--end-page", default=-1, type=int, help="Specify if you want to end at a specific page")
    parser.add_argument(
        "-q", "--input-question", default="Can you provide a summary of the context?", help="Question to ask"
    )
    parser.add_argument("-w", "--overwrite-index", action="store_true", help="Overwrite existing index")
    parser.add_argument("-t", "--train", action="store_true", help="Train and index the PDF file")
    parser.add_argument("-a", "--web-app", action="store_true", help="Start WebApp")
    parser.add_argument("-p", "--pre-process", action="store_true", help="Extract text from PDF file")
    parser.add_argument(
        "-b",
        "--embedding",
        choices=["openai", "huggingface", "huggingface-hub", "cohere"],
        default="openai",
        help="Embedding to use",
    )
    parser.add_argument(
        "-l",
        "--llm",
        choices=["openai", "huggingface"],
        default="openai",
        help="LLM to use",
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
    context = args.__dict__
    if args.web_app:
        run_web(context)
    elif args.train:
        run_workflow(context, training_workflow_steps())
    elif args.pre_process:
        run_workflow(context, pre_process_workflow_steps())
    else:
        run_workflow(context, workflow_steps())
        print("[bold]Question: " + context["input_question"] + "[/bold]")
        print("[blue]Answer: " + context["output"] + "[/blue]")


if __name__ == "__main__":  # pragma: no cover
    main()
