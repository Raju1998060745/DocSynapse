from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import  OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from uuid import uuid4
import os, glob
from .. import logger



def load_document(files_dir =""):
    '''
    Load document with file path
    '''
    try :
        if files_dir =="":
            files_dir = os.getenv('FILE_DOWNLOAD_PATH') 
        elif not os.path.exists(files_dir):
            raise FileNotFoundError(f'File Path {files_dir} does not exists')

        pdf_files = glob.glob(os.path.join(files_dir, "*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {files_dir}")
            return None
        all_documents = []
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                documents = loader.load()
                all_documents.extend(documents)
                logger.info(f"Successfully loaded {pdf_file}")
            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {e}")
        return all_documents
    except FileNotFoundError as e:
        logger.error(e)
        return e


def load_and_split_documents(filepath):
    '''
    Load AND Split document with file path
    '''
    try:
        documents = load_document(filepath)
        if not documents:
            logger.error("No documents found to load.")
            raise ValueError("No documents found to load.")
        else:
            split_docs = split_documents(documents)
            return split_docs
    except FileNotFoundError as e:
        return e
    except ValueError as e:
        return e


def split_documents(documents: list[Document]):
    '''
    Split document with file path  
    '''
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def embeding():
    embed = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    return embed

