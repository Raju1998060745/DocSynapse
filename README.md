# 📄 DocSynapse

**DocSynapse** is an intelligent document query platform that allows users to upload files (PDF, DOCX, etc.), and interact with their content using state-of-the-art Retrieval-Augmented Generation (RAG) techniques powered by **GROQ-backed LLMs**.

---

## 🔥 Features

- 🔐 **User authentication** (Login/Register)  
- 📁 **Upload and manage documents**  
- 🧠 **Query uploaded documents using RAG**  
- 🤖 **Multiple LLMs integrated via GROQ** for diverse answering styles  
- ⚡ **Fast, intelligent, and metadata-rich search** powered by vector stores  

---

## 🧱 Architecture Overview

### 🧩 Service-1: Ingestion Handler
- Detects new or updated files from document storage (e.g., AWS S3)
- Flags files for preprocessing:
  - **S1a**: New file → create new embeddings
  - **S1b**: Updated file → replace existing embeddings

### 🔎 Service-2: Processing and Storage
- Common logic to split and embed text
- Adds metadata (file name, page number, etc.)
- Stores or replaces entries in the vector store

### 🤝 Service-3: Query & Answer Engine
- Retrieves relevant chunks based on user query
- Uses GROQ to interact with different LLMs
- Returns intelligent responses using RAG

---

## 📦 Tech Stack

| Layer       | Tech Stack                             |
|------------|-----------------------------------------|
| Frontend   | React / Next.js (with Auth)             |
| Backend    | FastAPI                                 |
| Storage    | AWS S3 (pluggable provider)             |
| Vector Store | FAISS / Pinecone / Weaviate           |
| LLMs       | GROQ (Mix of models)                    |
| Database   | PostgreSQL / MongoDB (users)            |
| Embeddings | OpenAI / BGE / GROQ compatible          |

---

## 🧠 RAG Pipeline

1. Upload Document  
2. Document processed → split → embedded  
3. Stored in vector store  
4. User asks question  
5. Relevant chunks retrieved  
6. LLM generates answer using context  

---

## 🧪 TODOs / Future Enhancements

- [ ] Add support for more file types  
- [ ] Admin dashboard  
- [ ] Rate-limiting & usage tracking  
- [ ] Model selector (user picks GPT-4, Mixtral, Claude, etc.)  
- [ ] Streamed LLM responses  

---

## 🤝 Contributing

1. Fork this repo  
2. Clone your fork  
3. Create a feature branch  
4. Submit a PR and let’s build!  

---

## 🔄 System Architecture Diagram

```mermaid
flowchart TD
    %% External Components
    AWS_S3["AWS S3 (Cloud Storage)"]:::external
    LLM["LLM Providers"]:::external
    VSTORE["Vector Store"]:::external
    USERDB["User Database"]:::external
    USER["User"]:::external

    %% Ingestion Handler (Service-1)
    Ingestion_Handler["Ingestion Handler (Service-1)"]:::ingestion

    %% Processing & Storage (Service-2)
    subgraph "Processing & Storage (Service-2)"
        Service2_Entry["Service-2 Entry"]:::processing
        Service2_Wrapper["Service2 Wrapper"]:::processing
        Service2_API["API Endpoints"]:::api
        Service2_Process["Process Module"]:::core
        Service2_Retrieve["Retrieve Module"]:::core
        Service2_Models["Models Module"]:::core
        Service2_Exceptions["Exceptions Module"]:::core
        Service2_Config["Configuration/Logging"]:::config
    end

    %% Query & Answer Engine (Service-3)
    subgraph "Query & Answer Engine (Service-3)"
        Service3_Backend["Backend & UI"]:::query
        Service3_Static["Static Assets"]:::query
        Service3_Templates["Templates"]:::query
    end

    %% Data Flow Connections
    AWS_S3 -->|"upload_trigger"| Ingestion_Handler
    Ingestion_Handler -->|"triggers"| Service2_Entry
    Service2_Entry -->|"initiates_API"| Service2_API
    Service2_API -->|"calls_processing"| Service2_Process
    Service2_Process -->|"stores_embeddings"| VSTORE
    Service2_Process -->|"retrieves_sections"| Service2_Retrieve
    Service2_Retrieve -->|"returns_chunks"| Service2_API
    Service2_API -->|"optionally_wraps"| Service2_Wrapper

    %% User Query Flow
    USER -->|"visits"| Service3_Templates
    Service3_Templates -->|"renders_UI"| Service3_Backend
    Service3_Backend -->|"authenticates_with"| USERDB
    Service3_Backend -->|"queries_via_API"| Service2_API
    Service2_API -->|"fetches_docs"| Service2_Retrieve
    Service2_Retrieve -->|"queries_LLM"| LLM
    LLM -->|"returns_answer"| Service2_API
    Service3_Backend -->|"displays_response"| USER

    %% Styling Classes
    classDef ingestion fill:#f9c74f,stroke:#333,stroke-width:2px;
    classDef processing fill:#90be6d,stroke:#333,stroke-width:2px;
    classDef query fill:#f9844a,stroke:#333,stroke-width:2px;
    classDef external fill:#577590,stroke:#333,stroke-width:2px,color:#fff;
    classDef core fill:#277da1,stroke:#333,stroke-width:2px,color:#fff;
    classDef api fill:#f3722c,stroke:#333,stroke-width:2px,color:#fff;
    classDef config fill:#f94144,stroke:#333,stroke-width:2px,color:#fff;

    %% Click Events for Service-2 Components
    click Service2_API "https://github.com/raju1998060745/docsynapse/blob/main/service_2/api/user_routes.py"
    click Service2_Process "https://github.com/raju1998060745/docsynapse/blob/main/service_2/core/process.py"
    click Service2_Retrieve "https://github.com/raju1998060745/docsynapse/blob/main/service_2/core/retrieve.py"
    click Service2_Models "https://github.com/raju1998060745/docsynapse/blob/main/service_2/core/models.py"
    click Service2_Exceptions "https://github.com/raju1998060745/docsynapse/blob/main/service_2/core/exceptions.py"
    click Service2_Config "https://github.com/raju1998060745/docsynapse/blob/main/service_2/config/logger_config.py"
    click Service2_Entry "https://github.com/raju1998060745/docsynapse/blob/main/service_2/main.py"
    click Service2_Wrapper "https://github.com/raju1998060745/docsynapse/blob/main/service2.py"

    %% Click Events for Service-3 Components
    click Service3_Backend "https://github.com/raju1998060745/docsynapse/blob/main/service_3/app.py"
    click Service3_Static "https://github.com/raju1998060745/docsynapse/tree/main/service_3/static/"
    click Service3_Templates "https://github.com/raju1998060745/docsynapse/tree/main/service_3/templates/"
