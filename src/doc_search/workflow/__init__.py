import logging
import pickle
import shutil
from pathlib import Path
from typing import Any

import faiss  # type: ignore
import openai
from langchain import OpenAI, VectorDBQA
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings, HuggingFaceHubEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from py_executable_checklist.workflow import WorkflowBase, run_command
from pypdf import PdfReader
from rich import print
from slug import slug  # type: ignore

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


def pdf_to_faiss_db_path(app_dir: Path, input_pdf_path: Path, index_prefix_name: str) -> Path:
    output_dir = output_directory_for_pdf(app_dir, input_pdf_path) / f"{index_prefix_name}-index"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "index.pkl"


def pdf_to_index_path(app_dir: Path, input_pdf_path: Path, index_prefix_name: str) -> Path:
    output_dir = output_directory_for_pdf(app_dir, input_pdf_path) / f"{index_prefix_name}-index"
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
            convert_command = f"""convert -density 150 -background white -alpha remove -quality 100 -sharpen 0x1.0 {input_file_page} -quality 100 {image_path}"""
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
    pdf_images_path: Path

    def image_path_from_text_path(self, text_path: Path) -> Path:
        return self.pdf_images_path.joinpath(text_path.stem).with_suffix(".png")

    def execute(self) -> dict:
        source_chunks = []
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)

        for text_path in self.pages_text_path.glob("*.txt"):
            with open(text_path) as f:
                for text in text_splitter.split_text(f.read()):
                    if text:
                        source_chunks.append(
                            Document(page_content=text, metadata={"source": self.image_path_from_text_path(text_path)})
                        )

        return {"text_chunks": source_chunks}


class EmbeddingFromInput(WorkflowBase):
    """
    Select the embedding model from the given input
    """

    embedding: str
    hugging_face_model: str

    def execute(self) -> dict:
        embedding_api: Embeddings = OpenAIEmbeddings()
        index_prefix = self.embedding

        if self.embedding == "huggingface":
            embedding_api = HuggingFaceEmbeddings(model_name=self.hugging_face_model)
            index_prefix = f"{self.embedding}-{slug(self.hugging_face_model)}"
        elif self.embedding == "huggingface-hub":
            embedding_api = HuggingFaceHubEmbeddings(model_name=self.hugging_face_model)
            index_prefix = f"{self.embedding}-{slug(self.hugging_face_model)}"
        elif self.embedding == "cohere":
            embedding_api = CohereEmbeddings()

        return {"embedding_api": embedding_api, "index_prefix": index_prefix}


class CreateIndex(WorkflowBase):
    """
    Create index for embedding search
    """

    input_pdf_path: Path
    app_dir: Path
    overwrite_index: bool
    text_chunks: list[Document]
    embedding_api: Embeddings
    index_prefix: str

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def append_to_index(self, docsearch: VectorStore, doc: Document) -> None:
        docsearch.add_texts([doc.page_content], metadatas=[doc.metadata])

    def execute(self) -> dict:
        faiss_db = pdf_to_faiss_db_path(self.app_dir, self.input_pdf_path, self.index_prefix)
        index_path = pdf_to_index_path(self.app_dir, self.input_pdf_path, self.index_prefix)

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

        embeddings = self.embedding_api
        if isinstance(embeddings, OpenAIEmbeddings):
            docsearch: Any = FAISS.from_texts(
                [self.text_chunks[0].page_content], embeddings, metadatas=[self.text_chunks[0].metadata]
            )

            for chunk in self.text_chunks[1:]:
                self.append_to_index(docsearch, chunk)
        else:
            docsearch = FAISS.from_documents(self.text_chunks, embeddings)

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
        else:
            logging.info("Loading index from %s", self.faiss_db)

        index = faiss.read_index(self.index_path.as_posix())
        with open(self.faiss_db, "rb") as f:
            search_index = pickle.load(f)

        search_index.index = index
        return {"search_index": search_index}


class FindInputDocuments(WorkflowBase):
    """
    Find input documents by looking at the search index
    """

    search_index: Any
    input_question: str

    def execute(self) -> dict:
        input_documents = self.search_index.similarity_search(self.input_question, k=4)
        logging.info("Found %s documents", len(input_documents))
        for doc in input_documents:
            print(f"[bold]Source {doc.metadata['source']}[/bold]")

        # output
        return {"input_documents": input_documents}


class AskQuestion(WorkflowBase):
    """
    Ask question by sending prompt along with indexed data
    """

    input_question: str
    input_documents: list[Any]
    verbose: int

    def prompt_from_question(self) -> PromptTemplate:
        template = """
Instructions:
- Provide detailed response that relate to the question.
- If there is a code block in the answer then enclose it in triple backticks.
- Also tag the code block with the language name.

QUESTION: {question}
=========

{summaries}

ANSWER:"""

        return PromptTemplate(input_variables=["summaries", "question"], template=template)

    def execute(self) -> dict:
        question = self.input_question
        chain = load_qa_with_sources_chain(llm=OpenAI(), prompt=self.prompt_from_question(), verbose=self.verbose >= 1)
        output = chain(
            {
                "input_documents": self.input_documents,
                "question": question,
            }
        )
        output_text = output["output_text"]
        sources = [doc.metadata["source"] for doc in self.input_documents]
        return {"output": output_text, "sources": sources}

    @retry(exceptions=openai.error.RateLimitError, tries=2, delay=60, back_off=2)
    def send_prompt(self, qa: VectorDBQA, input_question: str) -> Any:
        return qa.run(query=input_question)


def training_workflow_steps() -> list:
    return [
        VerifyInputFile,
        ConvertPDFToImages,
        ConvertImagesToText,
        CombineAllText,
        EmbeddingFromInput,
        CreateIndex,
    ]


def find_input_documents_workflow() -> list:
    return training_workflow_steps() + [
        LoadIndex,
        FindInputDocuments,
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
        FindInputDocuments,
        AskQuestion,
    ]


def workflow_steps() -> list:
    return training_workflow_steps() + inference_workflow_steps()
