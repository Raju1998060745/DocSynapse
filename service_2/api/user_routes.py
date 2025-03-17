from langchain_ollama import OllamaEmbeddings
from service_2.core.process import load_and_split_documents, embeding
import os, glob
from langchain.schema import Document
from .. import logger
from langchain_chroma import Chroma
import chromadb
 

def rag_pull():
    '''
    retreive from related Vector store 
    '''
    # connect to db
    #  pull content 
    # return content
    pass



def embed_files(user_id: str, file_names :list[str] =None, files_dir: str = None):
    '''
    Load to related vectore store
    '''
    # check for file location and files
    try :
        if files_dir == None:
            files_dir = os.getenv('FILE_DOWNLOAD_PATH') 
            if not os.path.exists(files_dir):
                raise FileNotFoundError(f'File Directory {files_dir} does not exists')
        pdf_files= []
        missing_files =[]
        for i in file_names:
            if not os.path.exists(os.path.join(files_dir, f"{i}.pdf")):
                print(os.path.exists(os.path.join(files_dir, f"{i}.pdf")))
                missing_files.append(i)
                logger.debug(f"File not found {i}")
            else :
                pdf_files.append(os.path.join(files_dir, f"{i}.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f'Files {repr(file_names)} does not exists')
            

    # load and split

        documents = load_and_split_documents(pdf_files= pdf_files)

    # download embedding()
        # embeding = embeding()

    # add metadata 
        [doc.metadata.update({'user_id': user_id}) for doc in documents]


    # store to DB        
        chroma_db_init(collection=user_id,documents= documents)
        # return Success
        response = {
            'message': f"Successfully processed {len(pdf_files)} files.",
            'processed_files' : repr(pdf_files)
        }
        if missing_files:
            response['missing_files'] = repr(missing_files)
    
        return (response)

    except FileNotFoundError as e:
        return e
    except Exception as e:
        return e
    

def chroma_db_init(collection: str, documents: list[Document]):
    try:
        db_path =  os.getenv('DB_PATH') or 'service_2/db/chroma.db' 
        persistent_client = chromadb.PersistentClient(db_path)
        collection = persistent_client.get_or_create_collection(collection, embedding_function= OllamaEmbeddings(
        model="nomic-embed-text"
    ))
        collection.add(documents)
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to Load into Chrom db {str(e)}")
        

    
    
    


