from pathlib import Path

from py_executable_checklist.workflow import WorkflowBase, run_command


class ConvertImagesToText(WorkflowBase):
    """
    Convert images to text using tessaract OCR
    """

    pdf_images_path: Path
    input_pdf_path: Path
    app_dir: Path

    def execute(self) -> dict:
        pdf_file_name = self.input_pdf_path.stem
        output_dir = self.app_dir / "OutputDir/dr-doc-search" / pdf_file_name / "scanned"
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in self.pdf_images_path.glob("*.png"):
            image_name = image_path.stem
            text_path = output_dir / f"{image_name}"
            if text_path.exists():
                continue
            tesseract_command = f"tesseract {image_path} {text_path} --oem 1 -l eng"
            run_command(tesseract_command)

        return {"pages_text_path": output_dir}
