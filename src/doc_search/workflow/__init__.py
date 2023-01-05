from .convert_images_to_text import ConvertImagesToText
from .convert_pdf_to_pages import ConvertPDFToImages
from .verify_input_file import VerifyInputFile


def workflow_steps() -> list:
    return [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
    ]
