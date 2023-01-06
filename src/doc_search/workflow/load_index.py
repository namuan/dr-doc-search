import pickle
from pathlib import Path

import faiss  # type: ignore
from py_executable_checklist.workflow import WorkflowBase


class LoadIndex(WorkflowBase):
    """
    Load existing index for embedding search
    """

    index_path: Path
    faiss_db: Path

    def execute(self) -> dict:
        if not self.faiss_db.exists():
            raise FileNotFoundError(f"FAISS DB file not found: {self.faiss_db}")

        index = faiss.read_index(self.index_path.as_posix())
        with open(self.faiss_db, "rb") as f:
            search_index = pickle.load(f)

        search_index.index = index
        return {"search_index": search_index}
