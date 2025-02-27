from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import  OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader

import logging
from uuid import uuid4
from helper import load_config
import os



# def add_document_to_vector_store(docname):
#     loader = S3FileLoader("docsynapse-dev-stage", docname)
#     documents = loader.load()
#     return documents

logger =logging.getLogger(__name__)

vector_store = Chroma.from_documents(docs, embedding= embeding(), persist_directory=os.path.join(db_path,"chroma_db") )

def load_document(filepath ='Files'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    docsynapse_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    files_dir = os.path.join(docsynapse_root, filepath)
    if not os.path.exists(files_dir):
        logger.Error(f"Directory {files_dir} does not exist.")
        return None
    else:
        loader = PyPDFLoader(files_dir)
        documents = loader.load()
        return documents 


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