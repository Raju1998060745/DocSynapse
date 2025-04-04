
📄 DocSynapse
DocSynapse is an intelligent document query platform that allows users to upload files (PDF, DOCX, etc.), and interact with their content using state-of-the-art Retrieval-Augmented Generation (RAG) techniques powered by GROQ-backed LLMs.

🔥 Features
🔐 User authentication (Login/Register)

📁 Upload and manage documents

🧠 Query uploaded documents using RAG

🤖 Multiple LLMs integrated via GROQ for diverse answering styles

⚡ Fast, intelligent, and metadata-rich search powered by vector stores

🧱 Architecture Overview
🧩 Service-1: Ingestion Handler
Detects new or updated files from document storage (e.g., AWS S3)

Flags files for preprocessing:

S1a: New file → create new embeddings

S1b: Updated file → replace existing embeddings

🔎 Service-2: Processing and Storage
Common logic to split and embed text

Adds metadata (file name, page number, etc.)

Stores or replaces entries in the vector store

🤝 Service-3: Query & Answer Engine
Retrieves relevant chunks based on user query

Uses GROQ to interact with different LLMs

Returns intelligent responses using RAG

📦 Tech Stack
Layer	Tech Stack
Frontend	React / Next.js (with Auth)
Backend	FastAPI
Storage	AWS S3 (pluggable provider)
Vector Store	FAISS / Pinecone / Weaviate
LLMs	GROQ (Mix of models)
Database	PostgreSQL / MongoDB (users)
Embeddings	OpenAI / BGE / GROQ compatible

🧠 RAG Pipeline
Upload Document

Document processed → split → embedded

Stored in vector store

User asks question

Relevant chunks retrieved

LLM generates answer using context

🧪 TODOs / Future Enhancements
 Add support for more file types

 Admin dashboard

 Rate-limiting & usage tracking

 Model selector (user picks GPT-4, Mixtral, Claude, etc.)

 Streamed LLM responses

🤝 Contributing
Fork this repo

Clone your fork

Create a feature branch

Submit a PR and let’s build!
