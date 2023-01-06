from typing import Any

import openai
from langchain import OpenAI, VectorDBQA
from py_executable_checklist.workflow import WorkflowBase

from doc_search import retry


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
- Provide detailed responses that relate to the humans prompt.

Summarize text.
{selected_blocks}

- Human:
${question}

AI:"""

    def execute(self) -> dict:
        prompt = self.prompt_from_question(self.input_question, self.selected_blocks)
        qa = VectorDBQA.from_llm(llm=OpenAI(), vectorstore=self.search_index)
        output = self.send_prompt(prompt, qa)
        return {"output": output}

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def send_prompt(self, prompt: str, qa: VectorDBQA) -> Any:
        return qa.run(prompt)
