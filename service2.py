from service_2.utils.document_utils import load_and_split_documents, load_document,split_documents,embeding

from service_2 import logger
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
import os


db_path = 'service_2/db/chroma.db'

# documents = load_document(os.getenv('FILE_DOWNLOAD_PATH'))
# docs = split_documents(documents)
docs = load_and_split_documents(os.getenv('FILE_DOWNLOAD_PATH'))
# vector_store = Chroma.from_documents(docs, embedding= embeding(), persist_directory=db_path)



db = Chroma(persist_directory=db_path,embedding_function=embeding())
print("Number of documents in Chroma:", db._collection.count())
messages=[
   SystemMessage(content = "You are Ai Assistant, who is tasked to provide meaningful insigths based on question and retrieved knowledge"),
                ("human","Here are the relevant documents: {relevant_docs}"),
                ("human","{text}")
 ]
prompt_template = ChatPromptTemplate.from_messages(messages)
text = input("Enter your question: ")
retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.5},
)
relevant_docs = retriever.invoke(text)
print("relevant_docs", relevant_docs[0].page_content)
prompt = prompt_template.invoke({"relevant_docs": relevant_docs[0].page_content, "text": text})
# model = ChatOpenAI(model="gpt-3.5-turbo")
model = ChatOllama(model ="deepseek-r1:8b")
result = model.invoke(prompt)
print(result.content)

