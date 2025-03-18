from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma
from langchain_ollama import  OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from uuid import uuid4
import os, glob


from service_2.core.exceptions import DocumentLoadError, DocumentProcessingError, DocumentSplitError



import logging
logger = logging.getLogger(__name__) 

def load_document(pdf_files : list ):
    '''
    TODO: Make it private
Load document with file path
    '''
    try :
        
        all_documents = []
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                documents = loader.load()
                all_documents.extend(documents)
                logger.info(f"Successfully loaded {pdf_file}")
            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {str(e)}")
                raise DocumentLoadError(f"Failed to load {pdf_file}: {str(e)}")
        return all_documents
    except DocumentLoadError as e:
        logger.error(f"Document loading failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in load_document: {str(e)}")
        raise DocumentProcessingError(f"Unexpected error: {str(e)}")


def load_and_split_documents( pdf_files: list):
    '''
    Load AND Split document with file path
    '''
    try:
        documents = load_document(pdf_files)
        if not documents:
            logger.error("No documents found to load.")
            raise ValueError("No documents found to load.")
        else:
            split_docs = split_documents(documents)
            return split_docs
    except FileNotFoundError as e:
        return e
    except ValueError as e:
        return e
    except Exception as e:
        return e


def split_documents(documents: list[Document]):
    '''
    TODO: Make it private
    Split document with file path  
    '''
    try :

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        docs =text_splitter.split_documents(documents)
        if not docs:
            raise DocumentSplitError(f"Failed to SPlit Documents{uuid4()}: {str(e)}")
        return docs
    except DocumentSplitError as e:
        raise
    except FileNotFoundError as e:
        raise
    except ValueError as e:
        raise
    except Exception as e:
        raise DocumentSplitError(f"Failed to SPlit Documents {uuid4()}: {str(e)}")
    

def embedding():
    embed = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    return embed

def process_files(files_dir: str = None, file_names: list[str] = None) :
    try:
    # Validate inputs
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
        
        return pdf_files, missing_files
        
    except Exception as e:
        logger.error(f"File processing error: {str(e)}")
        raise DocumentProcessingError(f"Failed to process list of files: {str(e)}")
