from pathlib import Path
from typing import Any

from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import ConvertPDFToImages


def test_convert_pdf_to_pages() -> None:
    context: dict[str, Any] = {
        "input_pdf_path": Path("tests/data/input.pdf"),
        "pdf_pages": 2,
        "app_dir": Path(".") / "tests",
    }
    expected_output_path = Path("tests/OutputDir/dr-doc-search/input/images")

    run_workflow(context, [ConvertPDFToImages])

    assert context["pdf_images_path"] == expected_output_path
    assert len(list(expected_output_path.glob("*.png"))) == 2
