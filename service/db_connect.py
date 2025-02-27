import sqlite3
import os
import logging
from datetime import datetime, timezone


class DatabaseConnect():
    
    logger =logging.getLogger(__name__)
    def __init__(self, db_path='service/db/metadata.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        self.conn = self.initialize_db(self.db_path)
        self.logger.info("Database connection established")

    def close(self):
        self.conn.close()
        self.logger.info("Database connection closed")

    def initialize_db(self,db_path='service/db/metadata.db'):
        abs_db_path = os.path.abspath(db_path)
        # self.logger.debug("Absolute DB Path:", abs_db_path)
        # self. logger.debug("Working Directory:", os.getcwd())
        os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
        self.conn = sqlite3.connect(abs_db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS s3_objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT UNIQUE NOT NULL,
                last_modified TEXT NOT NULL
            )
            """)
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vector_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            s3_object_id INTEGER NOT NULL,
            vector_id TEXT,
            FOREIGN KEY (s3_object_id) REFERENCES s3_objects(id) ON DELETE CASCADE
        )
        ''')
        
        self.conn.commit()
        self.logger.info("Database initialized successfully")
        return self.conn



    def store_s3_objects_info(self,files_list):
        try:
            cursor =self.conn.cursor()
            response = files_list
            
            if not response :
                self.logger.warning("Response is empty or missing 'Contents' key.")
            
            for obj in response:
                key = obj['key']
                last_modified = obj['last_modified'].strftime('%Y-%m-%d %H:%M:%S')

                try:
                    cursor.execute("SELECT last_modified FROM s3_objects WHERE key_name = ?", (key,))
                    existing = cursor.fetchone()
                    if existing:
                        if existing[0] != last_modified:
                            cursor.execute("UPDATE s3_objects SET last_modified = ? WHERE key_name = ?", 
                                        (last_modified, key))
                            self.logger.info(f"Updated: {key}")
                    else:
                        cursor.execute("INSERT INTO s3_objects (key_name, last_modified) VALUES (?, ?)", 
                                    (key, last_modified))
                        self.logger.info(f"Inserted: {key}")
                except Exception as e:
                    self.logger.error(f"Failed to process {key}: {e}")
            self.conn.commit()

        except sqlite3.Error as e:
            self.logger.error(f"SQLite error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")


    def get_all_s3_objects(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT key_name, last_modified FROM s3_objects")
            rows = cursor.fetchall()
            
            files = []
            for row in rows:
                # Convert string datetime back to datetime object
                last_modified = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                last_modified = last_modified.replace(tzinfo=timezone.utc)
                
                files.append({
                    'key': row[0],
                    'size': 0,  # Size not stored in DB, default to 0
                    'last_modified': last_modified
                })
            
            return files
        
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving s3 objects: {e}")
            return []