import sqlite3
import logging
import boto3
import time
import uuid
from helper import load_config
from pinecone import Pinecone, ServerlessSpec
from data import embeding

from langchain_pinecone import PineconeVectorStore


# Configure logging
def get_documents_list():
    session = boto3.Session()  # Replace with your actual profile name

# Create S3 client using the session
    s3 = session.client('s3')

# Example operation to list buckets
    response = s3.list_objects_v2(Bucket='docsynapse-dev-stage')
    

    return response


def store_s3_objects_info():
    logging.basicConfig(filename="s3_db.log", level=logging.INFO, 
                        format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Connect to the database (or create it)
        conn = sqlite3.connect("s3Object.db")
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS s3_objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT UNIQUE NOT NULL,
            last_modified TEXT NOT NULL
        )
        """)

        # Fetch data
        response = get_documents_list()
        
        if not response or 'Contents' not in response:
            logging.warning("Response is empty or missing 'Contents' key.")

        # Insert or update data
        for obj in response.get('Contents', []):
            key = obj['Key']
            last_modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')

            try:
                # Check if key exists
                cursor.execute("SELECT last_modified FROM s3_objects WHERE key_name = ?", (key,))
                existing = cursor.fetchone()

                if existing:
                    # Update if timestamp is different
                    if existing[0] != last_modified:
                        cursor.execute("UPDATE s3_objects SET last_modified = ? WHERE key_name = ?", 
                                    (last_modified, key))
                        logging.info(f"Updated: {key}")
                else:
                    # Insert if key is not present
                    cursor.execute("INSERT INTO s3_objects (key_name, last_modified) VALUES (?, ?)", 
                                (key, last_modified))
                    logging.info(f"Inserted: {key}")

            except Exception as e:
                logging.error(f"Failed to process {key}: {e}")

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        # Close the connection safely
        if conn:
            conn.close()


def create_tracking_table():
    try:
        # Connect to the database (or create it)
        conn = sqlite3.connect("s3Object.db")
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doc_vector_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            docname TEXT NOT NULL,
            vector_id TEXT UNIQUE NOT NULL,
            FOREIGN KEY (docname) REFERENCES s3_objects(key_name)
        )
        """)

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        # Close the connection safely
        if conn:
            conn.close()


def pinecone_store():
    config =load_config()
    pinecone_api_key=config.get("PINECONE_API_KEY")
    print(pinecone_api_key)
    pc = Pinecone(api_key=pinecone_api_key)
    index_name = "docsynapses3v1"  # change if desired

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    return index

def assign_uuid_and_store(docname, chunks):
    logging.basicConfig(filename="s3_db.log", level=logging.INFO, 
                        format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Connect to the database (or create it)
        conn = sqlite3.connect("s3Object.db")
        cursor = conn.cursor()

        # Ensure the tracking table exists
        create_tracking_table()

        # Initialize Pinecone index
        index = pinecone_store()

        for chunk in chunks:
            vector_id = str(uuid.uuid4())
            
            vector_store = PineconeVectorStore(index=index, embedding=embeding())
            vector_store.aadd_texts(texts=chunk, ids=vector_id)
            # Store the chunk in the vector DB

            # Insert the docname and vector_id into the tracking table
            cursor.execute("""
            INSERT INTO doc_vector_tracking (docname, vector_id) VALUES (?, ?)
            """, (docname, vector_id))
            logging.info(f"Inserted vector_id {vector_id} for document {docname}")

        # Commit changes
        conn.commit()
        logging.info(f"Successfully committed changes for document {docname}")

    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        # Close the connection safely
        if conn:
            conn.close()
            logging.info("Database connection closed")
