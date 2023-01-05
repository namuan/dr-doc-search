from pathlib import Path
from typing import Any

from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import VerifyInputFile


def test_return_pdf_properties() -> None:
    context: dict[str, Any] = {
        "input_pdf_path": Path("tests/data/input.pdf"),
    }

    run_workflow(context, [VerifyInputFile])

    assert context["pdf_pages"] == 2
