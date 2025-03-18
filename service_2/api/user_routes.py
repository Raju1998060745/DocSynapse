
from service_2.core.process import load_and_split_documents, embeding,process_files
from service_2.core.exceptions import ChromaDBError
from service_2.core.retreive import chroma_db_embed,rag_pull_with_filter
from service_2.core.models import FileUploadRequest, RagRequestModel

import logging
logger = logging.getLogger(__name__)

def call_to_llm(data: RagRequestModel):
    '''TODO: Call chroma as retreiver and then call llm for ans'''



    results = rag_pull_with_filter(
        user_id=data.user,
        query=data.query,
        document_name=data.document_name or None
    )
    if not results:
        logger.info("No relevant documents found.")
        raise ValueError("No relevant documents found.")
    return results
    
    


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
        collection = chroma_db_embed(collection=user_id)
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
