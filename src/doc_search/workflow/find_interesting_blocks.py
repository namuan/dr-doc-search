from typing import Any

from py_executable_checklist.workflow import WorkflowBase


class FindInterestingBlocks(WorkflowBase):
    """
    Load existing index for embedding search
    """

    input_question: str
    search_index: Any

    def prompt_from_question(self, question: str) -> str:
        return f"""Instructions:
- You are a text based search engine.
- Provide keywords and summary which should be relevant to answer the question.
- Retain as much information as needed to answer the question later.

Question:
{question}"""

    def execute(self) -> dict:
        prompt = self.prompt_from_question(self.input_question)
        docs = self.search_index.similarity_search(prompt)
        return {"selected_blocks": docs[0].page_content}
