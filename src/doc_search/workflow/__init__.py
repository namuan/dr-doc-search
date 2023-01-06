from .ask_question import AskQuestion
from .combine_all_text import CombineAllText
from .convert_images_to_text import ConvertImagesToText
from .convert_pdf_to_pages import ConvertPDFToImages
from .create_index import CreateIndex
from .find_interesting_blocks import FindInterestingBlocks
from .load_index import LoadIndex
from .verify_input_file import VerifyInputFile


def workflow_steps() -> list:
    return [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
        CombineAllText,
        CreateIndex,
        LoadIndex,
        FindInterestingBlocks,
        AskQuestion,
    ]
