from typing import Any

from langchain import OpenAI, VectorDBQA
from py_executable_checklist.workflow import WorkflowBase


class AskQuestion(WorkflowBase):
    """
    Load existing index for embedding search
    """

    input_question: str
    selected_blocks: str
    search_index: Any

    def prompt_from_question(self, question: str, selected_blocks: str) -> str:
        return f"""
Instructions:
- Answer and guide the human when they ask for it.
- Provide comprehensive responses that relate to the humans prompt.

Summarize text.
{selected_blocks}

- Human:
${question}

AI:"""

    def execute(self) -> dict:
        prompt = self.prompt_from_question(self.input_question, self.selected_blocks)
        qa = VectorDBQA.from_llm(llm=OpenAI(), vectorstore=self.search_index)
        output = qa.run(prompt)
        return {"output": output}
