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


from service_2.api.user_routes import embed_files
from service_2.core.exceptions import DocumentLoadError, DocumentProcessingError, VectorStoreError

logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/home")
async def index( filename : str):
   return {"message": "Hello Worldhi "}


class FileUploadRequest(BaseModel):
    filename: list[str]
    user: str
    fileDirectory: str | None = None


@app.post('/api/files/upload')
async def upload_text(data: FileUploadRequest):
    try:
        # Validate request data
        if not data.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        if not data.user:
            raise HTTPException(status_code=400, detail="User is required")

        # Process files
        try:
            message = embed_files(
                user_id=data.user,
                file_names=data.filename,
                files_dir=data.fileDirectory
            )
            return {"response": message}
            
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
