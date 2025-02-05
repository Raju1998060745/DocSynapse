from langchain_community.document_loaders import S3FileLoader
from langchain_community.document_loaders import DropboxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
import boto3
from langchain_pinecone import PineconeVectorStore
from datastore import pinecone_store
from langchain_ollama import OllamaEmbeddings
from uuid import uuid4
from helper import load_config



def add_document_to_vector_store(key):
    loader = S3FileLoader("docsynapse-dev-stage", key)
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

def store_pinecone(documents):
    config =load_config()
    
    config.get("PINECONE_API_KEY") #TODO: STORE IN PINCEONE
    index=pinecone_store()
    

    vector_store = PineconeVectorStore(index=index, embedding=embeding())
    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)  # Add documents to the Pinecone index