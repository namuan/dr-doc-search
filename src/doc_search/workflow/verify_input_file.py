from pathlib import Path

from py_executable_checklist.workflow import WorkflowBase
from pypdf import PdfReader


class VerifyInputFile(WorkflowBase):
    """
    Verify input file and return pdf stats
    """

    input_pdf_path: Path

    def execute(self) -> dict:
        reader = PdfReader(self.input_pdf_path)

        # output
        return {
            "pdf_properties": {
                "pages": len(reader.pages),
            }
        }
