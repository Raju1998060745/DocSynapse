from flask import Flask, request, jsonify
from flask_login import login_required, current_user
import logging
import os
from langchain_groq import ChatGroq
from service_2.utils.document_utils import embeding
from service_2.utils.logger_utils import setup_logging
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate
from service_2.utils.document_utils import load_and_split_documents, load_document,split_documents,embeding
from service_2.utils.logger_utils import setup_logging
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize database
db_path = 'service_2/db/chroma.db'


# Load prompt template
messages = [
    SystemMessage(content="You are an AI Assistant, who is tasked to provide meaningful insights based on the question and retrieved knowledge."),
    ("human", "Here are the relevant documents: {relevant_docs}"),
    ("human", "{text}")
]
prompt_template = ChatPromptTemplate.from_messages(messages)

message = [
    SystemMessage(content="You are an AI Assistant, who is tasked to provide meaningful insights based on the question"),
    ("human", "{text}")
]
prompt_templates = ChatPromptTemplate.from_messages(messages)

@app.route('/api/files/upload', methods=['POST'])
def upload_text():
    try:
        logger = logging.getLogger(__name__)
        db_path = 'service_2/db/chroma.db'
        
        # Get the data from the request
        data = request.json
        
        # Extract text and filename
        filename = data.get("filename")
        username = data.get("user")
        
        if not filename:
            logger.error("No filename provided")
            return jsonify({"error": "Filename is required"}), 400
        
        # Process the text data
        try:
            
            # Create a Document object from the text
            doc = load_document(os.getenv('FILE_DOWNLOAD_PATH'))
            docs = split_documents(doc)
            db = Chroma(persist_directory=db_path, embedding_function=embeding(), collection_name=username)
            vector_store = db.from_documents(docs)      
            
            logger.info(f"Text content from {filename} processed for user {username}")
            
            return jsonify({
                "message": "Text processed successfully",
                "filename": filename,
                "username": username
            }), 200
            
        except Exception as e:
            logger.error(f"Error processing text content: {str(e)}")
            return jsonify({"error": f"Error processing text: {str(e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error handling text upload: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/messages', methods=['POST'])
def chat():
    try:
        # Get the user's question
        data = request.json
        text = data.get("text")
        print(text)
        username = data.get("user") # Get username from the logged-in user
        print(username)
        if not text:
            return jsonify({"error": "Text field is required"}), 400
        
        db = Chroma(persist_directory=db_path, embedding_function=embeding(), collection_name=username)

        # Retrieve relevant documents
        retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 20, "lambda_mult": 0.5},
        )
        relevant_docs = retriever.invoke(text)

        if not relevant_docs:
            prompt = prompt_templates.invoke({"text": text})
            return jsonify({"error": "No relevant documents found"}), 404

        # Prepare the prompt
        prompt = prompt_template.invoke({"relevant_docs": relevant_docs[0].page_content, "text": text})

        # Generate response using Ollama
        model = ChatGroq(temperature=0, groq_api_key="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", model_name="mixtral-8x7b-32768")
        result = model.invoke(prompt)

        # Return the response with the username
        return jsonify({
            "username": username,
            "response": result.content
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

    
