import logging
import pickle
import shutil
from pathlib import Path
from typing import Any

import faiss  # type: ignore
import openai
import torch
from langchain import OpenAI, VectorDBQA
from langchain.embeddings import HuggingFaceEmbeddings, HuggingFaceHubEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.base import BaseLLM
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from py_executable_checklist.workflow import WorkflowBase, run_command
from pypdf import PdfReader
from rich import print
from slug import slug  # type: ignore
from transformers import pipeline  # type: ignore

from doc_search import retry


def slugify_pdf_name(input_pdf_path: Path) -> str:
    return str(slug(input_pdf_path.stem))


def pdf_name_from(input_pdf_path: Path) -> str:
    return slugify_pdf_name(input_pdf_path)


def output_directory_for_pdf(app_dir: Path, input_pdf_path: Path) -> Path:
    pdf_file_name = pdf_name_from(input_pdf_path)
    return app_dir / "OutputDir/dr-doc-search" / pdf_file_name


def copy_raw_pdf_file(app_dir: Path, input_pdf_path: Path) -> Path:
    pdf_file_name = pdf_name_from(input_pdf_path)
    output_dir = app_dir / "OutputDir/dr-doc-search" / pdf_file_name
    output_dir.mkdir(parents=True, exist_ok=True)
    new_input_pdf_path = output_dir / f"{pdf_file_name}.pdf"
    if input_pdf_path != new_input_pdf_path:
        shutil.copyfile(input_pdf_path, new_input_pdf_path)
    return new_input_pdf_path


def pdf_to_faiss_db_path(app_dir: Path, input_pdf_path: Path) -> Path:
    output_dir = output_directory_for_pdf(app_dir, input_pdf_path) / "index"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "index.pkl"


def pdf_to_index_path(app_dir: Path, input_pdf_path: Path) -> Path:
    output_dir = output_directory_for_pdf(app_dir, input_pdf_path) / "index"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "docsearch.index"


class VerifyInputFile(WorkflowBase):
    """
    Verify input file and return pdf stats
    """

    app_dir: Path
    input_pdf_path: Path
    start_page: int
    end_page: int

    def execute(self) -> dict:
        new_pdf_file_path = copy_raw_pdf_file(self.app_dir, self.input_pdf_path)
        reader = PdfReader(new_pdf_file_path)
        total_pages = len(reader.pages)
        start_page = self.start_page if self.start_page != -1 else 1
        end_page = self.end_page if self.end_page != -1 else total_pages

        return {
            "input_pdf_path": new_pdf_file_path,
            "start_page": start_page,
            "end_page": end_page,
            "total_pages": total_pages,
        }


class ConvertPDFToImages(WorkflowBase):
    """
    Convert PDF to images using ImageMagick
    """

    input_pdf_path: Path
    app_dir: Path
    start_page: int
    end_page: int

    def execute(self) -> dict:
        output_dir = output_directory_for_pdf(self.app_dir, self.input_pdf_path) / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(self.start_page, self.end_page):
            input_file_page = f"{self.input_pdf_path}[{i}]"
            image_path = output_dir / f"output-{i}.png"
            if image_path.exists():
                continue
            convert_command = f"""convert -density 150 -trim -background white -alpha remove -quality 100 -sharpen 0x1.0 {input_file_page} -quality 100 {image_path}"""
            run_command(convert_command)

        return {"pdf_images_path": output_dir}


class ConvertImagesToText(WorkflowBase):
    """
    Convert images to text using tessaract OCR
    """

    pdf_images_path: Path
    input_pdf_path: Path
    app_dir: Path

    def execute(self) -> dict:
        output_dir = output_directory_for_pdf(self.app_dir, self.input_pdf_path) / "scanned"
        output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in self.pdf_images_path.glob("*.png"):
            image_name = image_path.stem
            text_path = output_dir / f"{image_name}"
            if text_path.with_suffix(".txt").exists():
                continue

            tesseract_command = f"tesseract {image_path} {text_path} --oem 1 -l eng"
            run_command(tesseract_command)

        return {"pages_text_path": output_dir}


class CombineAllText(WorkflowBase):
    """
    Combine all text files in the pages_text_path directory into one large text file and chunk it using Splitter
    """

    pages_text_path: Path

    def execute(self) -> dict:
        text = ""
        for file in self.pages_text_path.glob("*.txt"):
            text += file.read_text()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_text(text)

        return {
            "chunked_text_list": [t for t in texts if t],
        }


class CreateIndex(WorkflowBase):
    """
    Create index for embedding search
    """

    input_pdf_path: Path
    app_dir: Path
    overwrite_index: bool
    chunked_text_list: list[str]
    embedding: str

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def append_to_index(self, docsearch: FAISS, text: str, embeddings: Embeddings) -> None:
        docsearch.from_texts([text], embeddings)

    def embedding_from_selection(self) -> Embeddings:
        if self.embedding == "huggingface":
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        elif self.embedding == "huggingface-hub":
            return HuggingFaceHubEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        elif self.embedding == "cohere":
            return CohereEmbeddings()
        else:
            return OpenAIEmbeddings()

    def execute(self) -> dict:
        faiss_db = pdf_to_faiss_db_path(self.app_dir, self.input_pdf_path)
        index_path = pdf_to_index_path(self.app_dir, self.input_pdf_path)

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

        embeddings = self.embedding_from_selection()
        docsearch: FAISS = FAISS.from_texts(self.chunked_text_list[:2], embeddings)
        for text in self.chunked_text_list[2:]:
            self.append_to_index(docsearch, text, embeddings)

        faiss.write_index(docsearch.index, index_path.as_posix())
        with open(faiss_db, "wb") as f:
            pickle.dump(docsearch, f)

        return {"index_path": index_path, "faiss_db": faiss_db}


class LoadIndex(WorkflowBase):
    """
    Load existing index for embedding search
    """

    index_path: Path
    faiss_db: Path

    def execute(self) -> dict:
        if not self.faiss_db.exists():
            raise FileNotFoundError(f"FAISS DB file not found: {self.faiss_db}")

        print(f"[bold]Loading[/bold] index from {self.faiss_db}")
        index = faiss.read_index(self.index_path.as_posix())
        with open(self.faiss_db, "rb") as f:
            search_index = pickle.load(f)

        search_index.index = index
        return {"search_index": search_index}


class AskQuestion(WorkflowBase):
    """
    Ask question by sending prompt along with indexed data
    """

    input_question: str
    search_index: Any
    llm: str

    def prompt_from_question(self) -> PromptTemplate:
        template = """
Instructions:
- You are a text based search engine
- Provide keywords and summary which should be relevant to answer the question.
- Provide detailed responses that relate to the humans prompt.
- If there is a code block in the answer then wrap it in triple backticks.
- Also tag the code block with the language name.

{context}

- Human:
${question}

- You:"""

        return PromptTemplate(input_variables=["context", "question"], template=template)

    def llm_provider(self) -> BaseLLM:
        if self.llm == "huggingface":
            pipe = pipeline(
                "text2text-generation",
                model="pszemraj/long-t5-tglobal-base-16384-book-summary",
                device=0 if torch.cuda.is_available() else -1,
            )
            return HuggingFacePipeline(pipeline=pipe)
        else:
            return OpenAI()

    def execute(self) -> dict:
        llm = self.llm_provider()
        prompt = self.prompt_from_question()
        qa = VectorDBQA.from_llm(llm=llm, prompt=prompt, vectorstore=self.search_index)
        output = self.send_prompt(qa, self.input_question)
        return {"output": output}

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def send_prompt(self, qa: VectorDBQA, input_question: str) -> Any:
        return qa.run(query=input_question)


def training_workflow_steps() -> list:
    return [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
        CombineAllText,
        CreateIndex,
    ]


def pre_process_workflow_steps() -> list:
    return [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
    ]


def inference_workflow_steps() -> list:
    return [
        LoadIndex,
        AskQuestion,
    ]


def workflow_steps() -> list:
    return training_workflow_steps() + inference_workflow_steps()
