
from service_2.core.process import load_and_split_documents,process_files
from service_2.core.exceptions import ChromaDBError
from service_2.core.retrieve import chroma_db_embed,rag_pull_with_filter, chroma_db_retrieve
from service_2.core.models import FileUploadRequest, RagRequestModel
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate
import os


import logging
logger = logging.getLogger(__name__)

def call_to_llm(data: RagRequestModel):
    '''TODO: Call chroma as retrieve and then call llm for ans'''



    results = rag_pull_with_filter(
        user_id=data.user,
        query=data.query,
        document_name=data.document_name or None
    )

    text=data.query

    if not results:
        logger.info("No relevant documents found.")
        raise ValueError("No relevant documents found.")

    #TODO: Call LLM with results
    messages = [
        SystemMessage(content="You are an AI Assistant, who is tasked to provide meaningful insights based on the question and retrieved knowledge."),
        ("human", "Here are the relevant documents: {relevant_docs}"),
        ("human", "{text}")
    ]
    prompt_template = ChatPromptTemplate.from_messages(messages)
    
    prompt = prompt_template.invoke({"relevant_docs": results[0].page_content, "text": text})

    model = ChatGroq(temperature=0, groq_api_key=os.getenv('GROQ_API_KEY'), model_name="llama-3.3-70b-versatile")
    result = model.invoke(prompt)
    print(result)

    return result

    

def delete_collection(user_id: str, document:str =None):
    try:
        collection = chroma_db_retrieve(user_id)
        if document:
            collection.delete(
                where={'source': document}
            )
        else:
            collection.delete( where={'user_id': user_id})
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise ChromaDBError(f"Failed to delete collection: {str(e)}")
def embed_files(user_id: str, file_names: list[str] = None, files_dir: str = None) -> dict:
    """
    Load and embed documents into vector store

    """
    try:        
        # Validate inputs
        pdf_files, missing_files = process_files( files_dir=files_dir, file_names=file_names)   


        # Load and process documents
        documents = load_and_split_documents(pdf_files=pdf_files)
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                'user_id': user_id
            })
            
        # Store in ChromaDB
        collection = chroma_db_embed(user_id)
        collection.add_documents(documents)
        
        # Prepare response
        response = {
            'status': 'success',
            'message': f"Successfully processed {len(pdf_files)} files",
            'processed_files': pdf_files,
            'document_count': len(documents)
        }
        
        if missing_files:
            response['missing_files'] = missing_files
            
        return response
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise ChromaDBError(f"Document processing failed: {str(e)}")
