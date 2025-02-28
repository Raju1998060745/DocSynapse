from service_2.utils.document_utils import load_and_split_documents, load_document,split_documents,embeding
from service_2.utils.logger_utils import setup_logging
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import logging
import os
setup_logging()

logger =logging.getLogger(__name__)
db_path = 'service_2/db/chroma.db'

# documents = load_document(os.getenv('FILE_DOWNLOAD_PATH'))
# docs = split_documents(documents)
# vector_store = Chroma.from_documents(docs, embedding= embeding(), persist_directory=db_path)



db = Chroma(persist_directory=db_path,embedding_function=embeding())
retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.5},
)

print("Number of documents in Chroma:", db._collection.count())

relevant_docs = retriever.invoke("what did manish do?")
print("relevant_docs", relevant_docs)

