import logging
import pickle
from pathlib import Path

import faiss  # type: ignore
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from py_executable_checklist.workflow import WorkflowBase

from doc_search import retry


class CreateIndex(WorkflowBase):
    """
    Create index for embedding search
    """

    input_pdf_path: Path
    app_dir: Path
    overwrite_index: bool
    chunked_text_list: list[str]

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def append_to_index(self, docsearch: FAISS, text: str, embeddings: OpenAIEmbeddings) -> None:
        docsearch.from_texts([text], embeddings)

    def execute(self) -> dict:
        pdf_file_name = self.input_pdf_path.stem
        output_dir = self.app_dir / "OutputDir/dr-doc-search" / pdf_file_name / "index"
        output_dir.mkdir(parents=True, exist_ok=True)
        faiss_db = output_dir / "index.pkl"
        index_path = output_dir / "docsearch.index"

        if not self.overwrite_index and faiss_db.exists():
            logging.info("Index already exists at %s", faiss_db)
            return {"index_path": index_path, "faiss_db": faiss_db}
        else:
            logging.info(
                "Creating index at %s either because overwrite_index == %s or index file exists == %s",
                faiss_db,
                self.overwrite_index,
                faiss_db.exists(),
            )

        embeddings = OpenAIEmbeddings()
        docsearch: FAISS = FAISS.from_texts(self.chunked_text_list[:2], embeddings)
        for text in self.chunked_text_list[2:]:
            self.append_to_index(docsearch, text, embeddings)

        faiss.write_index(docsearch.index, index_path.as_posix())
        with open(faiss_db, "wb") as f:
            pickle.dump(docsearch, f)

        return {"index_path": index_path, "faiss_db": faiss_db}
