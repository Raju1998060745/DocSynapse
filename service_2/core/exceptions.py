class DocumentProcessingError(Exception):
    """Base exception for document processing errors"""
    pass

class DocumentLoadError(DocumentProcessingError):
    """Raised when document loading fails"""
    pass

class DocumentSplitError(DocumentProcessingError):
    """Raised when document splitting fails"""
    pass

class EmbeddingError(DocumentProcessingError):
    """Raised when embedding generation fails"""
    pass

class VectorStoreError(DocumentProcessingError):
    """Raised when vector store operations fail"""
    pass

class ChromaDBError(Exception):
    """Base exception for ChromaDB operations"""
    pass

class DocumentNotFoundError(ChromaDBError):
    """Raised when documents are not found"""
    pass

class EmbeddingError(ChromaDBError):
    """Raised when embedding operations fail"""
    pass