from pathlib import Path

from py_executable_checklist.workflow import WorkflowBase, run_command


class ConvertPDFToImages(WorkflowBase):
    """
    Convert PDF to images using ImageMagick
    """

    input_pdf_path: Path
    pdf_pages: int
    app_dir: Path

    def execute(self) -> dict:
        pdf_file_name = self.input_pdf_path.stem
        output_dir = self.app_dir / "OutputDir/dr-doc-search" / pdf_file_name / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(self.pdf_pages):
            input_file_page = f"{self.input_pdf_path}[{i}]"
            image_path = output_dir / f"output-{i}.png"
            if image_path.exists():
                continue
            convert_command = f"""convert -density 150 -trim -background white -alpha remove -quality 100 -sharpen 0x1.0 {input_file_page} -quality 100 {image_path}"""
            run_command(convert_command)

        return {"pdf_images_path": output_dir}
