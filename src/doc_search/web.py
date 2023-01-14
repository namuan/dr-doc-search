import logging
from typing import Any

import panel
import panel as pn
from py_executable_checklist.workflow import run_workflow

from doc_search.workflow import (
    inference_workflow_steps,
    pdf_name_from,
    pdf_to_faiss_db_path,
    pdf_to_index_path,
)

pn.extension(loading_spinner="dots", loading_color="#00aa41")

txt_input = pn.widgets.TextInput(value="", placeholder="Enter text here...", sizing_mode="stretch_width")
btn_ask = pn.widgets.Button(name="Ask me something!", width=100)
panel_conversations = []  # store all panel objects in a list
global_context = {}  # store workflow context


def add_qa_to_panel(question: str, answer: str) -> None:
    qa_block = f"""
🙂    **{question}**

📖    {answer}
    """
    panel_conversations.append(
        pn.Row(
            pn.pane.Markdown(
                qa_block,
                width=600,
                style={
                    "background-color": "#F6F6F6",
                    "line-height": "1.5",
                },
            ),
        )
    )


def get_conversations(_: Any) -> pn.Column:
    prompt = txt_input.value_input
    logging.info("Getting conversation for prompt: %s for input %s", prompt, txt_input)
    if prompt != "":
        input_question = global_context["input_question"] = prompt
        run_workflow(global_context, inference_workflow_steps())
        openai_answer = global_context["output"]
        logging.info("Answer: %s", openai_answer)
        add_qa_to_panel(input_question, openai_answer)
    txt_input.value_input = ""
    return pn.Column(*(reversed(panel_conversations)))


def run_inference_workflow(context: dict) -> None:
    run_workflow(context, inference_workflow_steps())


def run_web(context: dict) -> None:
    global global_context
    context["index_path"] = pdf_to_index_path(context["app_dir"], context["input_pdf_path"])
    context["faiss_db"] = pdf_to_faiss_db_path(context["app_dir"], context["input_pdf_path"])
    global_context = context
    interactive_conversation = pn.bind(get_conversations, btn_ask)

    pdf_name = pdf_name_from(context["input_pdf_path"])
    panel_conversations.append(
        pn.pane.Markdown(f"📖 Ask me something about {pdf_name}", width=600, style={"background-color": "#F6F6F6"}),
    )

    run_workflow(global_context, inference_workflow_steps())
    add_qa_to_panel("*Here is the book summary*", global_context["output"])

    dashboard = pn.Column(
        pn.Row(txt_input, btn_ask),
        pn.panel(
            interactive_conversation,
            loading_indicator=True,
            height=500,
            style={"border-radius": "5px", "border": "1px black solid"},
        ),
    )
    panel.serve(dashboard, port=5006, show=True)
