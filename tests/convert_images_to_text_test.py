from pathlib import Path
from typing import Any

from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import ConvertImagesToText


def test_images_to_text() -> None:
    context: dict[str, Any] = {
        "input_pdf_path": Path("tests/data/input.pdf"),
        "pdf_images_path": Path("tests/data/images/"),
        "app_dir": Path(".") / "tests",
    }
    expected_output_path = Path("tests/OutputDir/dr-doc-search/input/scanned")

    run_workflow(context, [ConvertImagesToText])

    assert context["pages_text_path"] == expected_output_path
    assert len(list(expected_output_path.glob("*.txt"))) == 2
