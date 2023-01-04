import logging
from pathlib import Path

from py_executable_checklist.workflow import WorkflowBase


class DoSomething(WorkflowBase):
    """
    Do Something here
    """

    input_pdf_path: Path

    def execute(self) -> dict:
        logging.info("Load %s", self.input_pdf_path)

        # output
        return {"output_file": f"Hello {self.input_pdf_path.as_posix()}"}
