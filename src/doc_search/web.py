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

inp = pn.widgets.TextInput(value="", placeholder="Enter text here...")
button_conversation = pn.widgets.Button(name="Ask me something!")
convos_text = []  # store all texts in a list
convos = []  # store all panel objects in a list
global_context = {}  # store workflow context


def get_conversations(_: Any) -> pn.Column:
    prompt = inp.value_input
    logging.info("Getting conversation for prompt: %s for input %s", prompt, inp)
    if prompt != "":
        input_question = global_context["input_question"] = prompt
        convos_text.append(input_question)
        run_workflow(global_context, inference_workflow_steps())
        openai_answer = global_context["output"]
        logging.info("Answer: %s", openai_answer)
        convos_text.append(openai_answer)
        convos.append(pn.Row("🙂", pn.pane.Markdown(f"**{prompt}**", width=600)))
        convos.append(pn.Row("📖", pn.pane.Markdown(openai_answer, width=600, style={"background-color": "#F6F6F6"})))
    inp.value_input = ""
    return pn.Column(*convos)


def run_inference_workflow(context: dict) -> None:
    run_workflow(context, inference_workflow_steps())


def run_web(context: dict) -> None:
    global global_context
    context["index_path"] = pdf_to_index_path(context["app_dir"], context["input_pdf_path"])
    context["faiss_db"] = pdf_to_faiss_db_path(context["app_dir"], context["input_pdf_path"])
    global_context = context
    interactive_conversation = pn.bind(get_conversations, button_conversation)

    pdf_name = pdf_name_from(context["input_pdf_path"])
    convos.append(
        pn.Row(
            "📖",
            pn.pane.Markdown(f"Ask me something about {pdf_name}", width=600, style={"background-color": "#F6F6F6"}),
        )
    )

    run_workflow(global_context, inference_workflow_steps())

    convos.append(pn.Row("📖", pn.pane.Markdown("**Here is the book summary**", width=600)))
    convos.append(
        pn.Row("📖", pn.pane.Markdown(global_context["output"], width=600, style={"background-color": "#F6F6F6"}))
    )

    dashboard = pn.Column(
        inp,
        pn.Row(button_conversation),
        pn.panel(interactive_conversation, loading_indicator=True, height=500),
    )
    panel.serve(dashboard, port=5006, show=True)
