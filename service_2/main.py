from fastapi import FastAPI, HTTPException


from flask import Flask, request, jsonify
import os
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
import logging


from service_2.api.user_routes import embed_files, call_to_llm, delete_collection
from service_2.core.exceptions import DocumentLoadError, DocumentProcessingError, VectorStoreError
from service_2.core.models import FileUploadRequest, RagRequestModel, CollectionNameRequest
from service_2 import logger  

logger = logging.getLogger(__name__)

app = FastAPI()


logger.info("Starting FastAPI application...")
@app.get("/home")
async def index( ):
   return {"message": f"Hello Worldhi"}





@app.post('/api/files/upload')
async def upload_text(data: FileUploadRequest):
    try:
        if not data.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        if not data.user:
            raise HTTPException(status_code=400, detail="User is required")

        try:
            message = embed_files(
                user_id=data.user,
                file_names=data.filename,
                files_dir=data.fileDirectory
            )
            
            if isinstance(message, Exception):
                if isinstance(message, FileNotFoundError):
                    raise HTTPException(status_code=404, detail=str(message))
                raise HTTPException(status_code=500, detail=str(message))
                
            return {"status": "success", "response": message}
            
        except DocumentLoadError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DocumentProcessingError as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred"
        )

@app.post('/api/rag')
async def get_rag_response(data: RagRequestModel):
    """
    Retrieve RAG responses from ChromaDB
    """
    try:
        # Validate request data
        if not data.user:
            raise HTTPException(status_code=400, detail="User is required")
        if not data.query:
            raise HTTPException(status_code=400, detail="Query is required")

        try:
            # Get results from ChromaDB
            results = call_to_llm(
                data)

            

            # Format response
            response = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in results
            ]
            
            return {
                "status": "success",
                "results": response,
                "count": len(response)
            }
            
        except VectorStoreError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"Vector store error: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in RAG endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while processing your query{str(e)}"
        )


@app.post('/api/delete')
async def delete(data: CollectionNameRequest):

    if not data.user:
        raise HTTPException(status_code=400, detail="User is required")
       
    try:
        print('1')
        delete_collection(
            user_id=data.user,
            document=data.document_name or None
        )
        return {"status": "success", "message": "Collection deleted successfully"}
    except Exception as e:
        logger.error(f"Unexpected error in delete_Collection: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while deleting the collection{str(e)}"
        )