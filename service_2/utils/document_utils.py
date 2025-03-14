from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import  OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from uuid import uuid4

import os, glob, logging



# def add_document_to_vector_store(docname):
#     loader = S3FileLoader("docsynapse-dev-stage", docname)
#     documents = loader.load()
#     return documents

logger =logging.getLogger(__name__)


def load_document(files_dir =""):
    
    if files_dir =="":
        files_dir = os.getenv('FILE_DOWNLOAD_PATH') 
    
    pdf_files = glob.glob(os.path.join(files_dir, "*.pdf"))
    print(pdf_files)
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

def load_and_split_documents(filepath):
    documents = load_document(filepath)
    if not documents:
        logger.error("No documents found to load.")
        return None
    else:
        split_docs = split_documents(documents)
        return split_docs

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def embeding():
    embed = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    return embed

# def store_pinecone(index,documents,vector_id):
#     config =load_config()
    
#     config.get("PINECONE_API_KEY") #TODO: STORE IN PINCEONE
    

#       # Add documents to the Pinecone index

t=load_document()