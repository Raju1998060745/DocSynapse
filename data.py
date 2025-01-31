from langchain_community.document_loaders import S3FileLoader
from langchain_community.document_loaders import DropboxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
import boto3
from langchain_ollama import OllamaEmbeddings
from helper import load_config

def get_documents_list():
    session = boto3.Session()  # Replace with your actual profile name

# Create S3 client using the session
    s3 = session.client('s3')

# Example operation to list buckets
    response = s3.list_objects_v2(Bucket='docsynapse-dev-stage')

    return response

def load_documents():
    loader = S3FileLoader("docsynapse-dev-stage", "All Vendor list.pdf")
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

def store_pinecone():
    config =load_config()
    config.get("PINECONE_API_KEY") #TODO: STORE IN PINCEONE
