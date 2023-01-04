from pathlib import Path

from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import DoSomething


def test_return_input_pdf_file() -> None:
    context = {
        "input_pdf_path": Path("tests/data/input.pdf"),
    }

    run_workflow(context, [DoSomething])

    assert context["output_file"] == "Hello tests/data/input.pdf"
