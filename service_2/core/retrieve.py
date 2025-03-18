from  langchain_chroma import Chroma
import os
import chromadb
from service_2.core.process import embedding
from service_2.core.exceptions import ChromaDBError
import logging
logger = logging.getLogger(__name__)


def rag_pull_with_filter(user_id: str, query: str, document_name: str = None, k: int = 2):
    """
    Retrieve filtered documents from vector store
    """
    try:
        collection = chroma_db_retrieve(collection_name=user_id)
        filter_dict = {'user_id': user_id}
        if document_name:
            filter_dict['source'] = document_name    
        results = collection.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        print(repr(results))
        if not results:
            logger.info(f"No results found for user {user_id}")
            return []
        return results
    
    except ChromaDBError as e:
        logger.error(f"ChromaDB operation failed: {str(e)}")
        raise  # Re-raise the original error without wrapping

def chroma_db_retrieve(collection_name: str):
    """
    Initialize ChromaDB client and get collection
    """
    try:
        
        db_path = os.getenv('DB_PATH') or 'service_2/db/chroma.db'
        persistent_client = chromadb.PersistentClient(db_path)
        collection = persistent_client.get_collection(
            collection_name
        )
        logger.info(f"Found existing collection: {collection_name}")
        db = Chroma(
        persist_directory=db_path,
        embedding_function=embedding(),
        collection_name=collection_name)
        return db
        
    except ValueError as e:
        logger.error(f"ChromaDB operation failed: {str(e)}")
        raise ChromaDBError(str(e))
    except Exception as e:
        logger.info(f"Unexpected Error while collection retrieval: {str(e)}")
        raise 


def chroma_db_embed(collection_name: str):
    try:
        db_path =  os.getenv('DB_PATH') or 'service_2/db/chroma.db' 
        # persistent_client = chromadb.PersistentClient(db_path)
        # collection = persistent_client.get_or_create_collection(collection, embedding_function= OllamaEmbeddings(
        # model="nomic-embed-text"))
        db = Chroma(
        persist_directory=db_path,
        embedding_function=embedding(),
        collection_name=collection_name)
        
        return db
    except Exception as e:
        raise RuntimeError(f"Failed to connect into Chrom db {str(e)}")
