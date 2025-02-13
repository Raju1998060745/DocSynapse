from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from uuid import uuid4
from helper import load_config



def add_document_to_vector_store(docname):
    loader = S3FileLoader("docsynapse-dev-stage", docname)
    documents = loader.load()
    return documents


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
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