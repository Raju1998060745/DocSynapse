from langchain_ollama import OllamaEmbeddings
from service_2.core.process import load_and_split_documents, embeding
import os, glob
from langchain.schema import Document
from .. import logger
from langchain_chroma import Chroma
import chromadb
from service_2.core.exceptions import *


def Call_to_LLM():
    '''TODO: Call chroma as retreiver and then call llm for ans'''
    pass

def rag_pull(user_id: str, query: str, k: int = 2):
    """
    Retrieve documents from vector store
    
    Args:
        user_id (str): User identifier
        query (str): Search query
        k (int): Number of results to return
        
    Returns:
        list: Matching documents
        
    Raises:
        ChromaDBError: If retrieval fails
    """
    try:
        collection = chroma_db_init(collection=user_id)
        results = collection.similarity_search(
            query=query, 
            k=k
        )
        return results
        
    except Exception as e:
        logger.error(f"RAG pull failed: {str(e)}")
        raise ChromaDBError(f"Failed to retrieve documents: {str(e)}")

def rag_pull_with_filter(user_id: str, query: str, document_name: str = None, k: int = 2):
    """
    Retrieve filtered documents from vector store
    
    Args:
        user_id (str): User identifier
        query (str): Search query
        document_name (str, optional): Document name to filter by
        k (int): Number of results to return
        
    Returns:
        list: Matching documents
    """
    try:
        collection = chroma_db_init(collection=user_id)
        filter_dict = {'user_id': user_id}
        
        if document_name:
            filter_dict['source'] = document_name
            
        results = collection.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        return results
        
    except Exception as e:
        logger.error(f"RAG pull with filter failed: {str(e)}")
        raise ChromaDBError(f"Failed to retrieve filtered documents: {str(e)}")


def embed_files(user_id: str, file_names: list[str] = None, files_dir: str = None) -> dict:
    """
    Load and embed documents into vector store
    
    Args:
        user_id (str): User identifier
        file_names (list[str]): List of file names to process
        files_dir (str, optional): Directory containing files
        
    Returns:
        dict: Processing results
        
    Raises:
        FileNotFoundError: If files or directory not found
        ChromaDBError: If embedding or storage fails
    """
    try:
        # Validate inputs
        if not user_id or not file_names:
            raise ValueError("User ID and file names are required")
            
        files_dir = files_dir or os.getenv('FILE_DOWNLOAD_PATH')
        if not os.path.exists(files_dir):
            raise FileNotFoundError(f'Directory not found: {files_dir}')
            
        # Process files
        pdf_files = []
        missing_files = []
        
        for filename in file_names:
            file_path = os.path.join(files_dir, f"{filename}.pdf")
            if os.path.exists(file_path):
                pdf_files.append(file_path)
            else:
                missing_files.append(filename)
                logger.warning(f"File not found: {filename}")
                
        if not pdf_files:
            raise FileNotFoundError(f'No valid files found from: {file_names}')
            
        # Load and process documents
        documents = load_and_split_documents(pdf_files=pdf_files)
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                'user_id': user_id,
                'processed_date': datetime.now().isoformat()
            })
            
        # Store in ChromaDB
        collection = chroma_db_init(collection=user_id)
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

def chroma_db_init(collection: str):
    try:
        db_path =  os.getenv('DB_PATH') or 'service_2/db/chroma.db' 
        # persistent_client = chromadb.PersistentClient(db_path)
        # collection = persistent_client.get_or_create_collection(collection, embedding_function= OllamaEmbeddings(
        # model="nomic-embed-text"))
        db = Chroma(
        persist_directory=db_path,
        embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
        collection_name=collection)

        
    
        
        return db
    except Exception as e:
        raise RuntimeError(f"Failed to connect into Chrom db {str(e)}")







