from pathlib import Path

from langchain.text_splitter import CharacterTextSplitter
from py_executable_checklist.workflow import WorkflowBase


class CombineAllText(WorkflowBase):
    """
    Combine all text files in the pages_text_path directory into one large text file and chunk it using Splitter
    """

    pages_text_path: Path

    def execute(self) -> dict:
        text = ""
        for file in self.pages_text_path.glob("*.txt"):
            text += file.read_text()

        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        texts = text_splitter.split_text(text)

        return {
            "chunked_text_list": texts,
        }
