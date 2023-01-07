from pathlib import Path
from typing import Any

from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import VerifyInputFile


def test_return_pdf_properties() -> None:
    context: dict[str, Any] = {
        "app_dir": Path.cwd(),
        "input_pdf_path": Path("tests/data/input.pdf"),
        "start_page": -1,
        "end_page": -1,
    }

    run_workflow(context, [VerifyInputFile])

    assert context["start_page"] == 1
    assert context["end_page"] == 2
    assert context["total_pages"] == 2


def test_override_start_and_end_pages() -> None:
    context: dict[str, Any] = {
        "app_dir": Path.cwd(),
        "input_pdf_path": Path("tests/data/input.pdf"),
        "start_page": 2,
        "end_page": 2,
    }

    run_workflow(context, [VerifyInputFile])

    assert context["start_page"] == 2
    assert context["end_page"] == 2
    assert context["total_pages"] == 2
