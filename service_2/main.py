from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from flask import Flask, request, jsonify
import os
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
import logging


from service_2.api.user_routes import embed_files, rag_pull, rag_pull_with_filter
from service_2.core.exceptions import DocumentLoadError, DocumentProcessingError, VectorStoreError

logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/home")
async def index( ):
   return {"message": f"Hello Worldhi"}


class FileUploadRequest(BaseModel):
    filename: list[str]
    user: str
    fileDirectory: str | None = None
    
class RagRequestModel(BaseModel):
    user: str
    query: str
    document_name: str | None = None


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
            if data.document_name:
                results = rag_pull_with_filter(
                    user_id=data.user,
                    query=data.query,
                    document_name=data.document_name
                )
            else:
                results = rag_pull(
                    user_id=data.user,
                    query=data.query
                )

            # Check if results are empty
            if not results:
                return {
                    "status": "success",
                    "message": "No matching documents found",
                    "results": [],
                    "count": 0
                }

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
            detail="An unexpected error occurred while processing your query"
        )


 
# @app.route('/api/messages', methods=['POST'])
# def chat():
#     try:
#         # Get the user's question
#         data = request.json
#         text = data.get("text")
#         print(text)
#         username = data.get("user") # Get username from the logged-in user
#         print(username)
#         if not text:
#             return jsonify({"error": "Text field is required"}), 400
       
#         db = Chroma(persist_directory=db_path, embedding_function=embeding(), collection_name=username)

 
#         # Return the response with the username
#         return jsonify({
#             "username": username,
#             "response": result.content
#         })
 
#     except Exception as e:
#         logger.error(f"Error processing request: {str(e)}")
#         return jsonify({"error": "Internal Server Error"}), 500
