from pathlib import Path

from py_executable_checklist.workflow import WorkflowBase
from pypdf import PdfReader


class VerifyInputFile(WorkflowBase):
    """
    Verify input file and return pdf stats
    """

    input_pdf_path: Path
    start_page: int
    end_page: int

    def execute(self) -> dict:
        reader = PdfReader(self.input_pdf_path)
        total_pages = len(reader.pages)
        start_page = self.start_page if self.start_page != -1 else 1
        end_page = self.end_page if self.end_page != -1 else total_pages

        return {"start_page": start_page, "end_page": end_page, "total_pages": total_pages}
