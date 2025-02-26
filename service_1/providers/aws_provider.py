import boto3
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class AWSProvider():
    def __init__(self):
        self.session = boto3.Session()
        self.s3 = self.session.client('s3')

    def list_all_files(self,bucket_name, prefix=''):
        logger.info(f"Listing files in bucket: {bucket_name} with prefix: {prefix}")
        files = []
        paginator = self.s3.get_paginator('list_objects_v2')
        try:
            # Paginate through results since S3 limits to 1000 objects per request
            for page in paginator.paginate(Bucket=bucket_name , Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified']
                        })
            return files
        except Exception as e:
            logger.info(f"Error listing files in bucket {bucket_name}: {str(e)}")
            return []

    def download_files(self, bucket_name, key='', local_path=None):
        try:
            if local_path is None:
                local_path = os.getenv('FILE_DOWNLOAD_PATH')
        
            if not bucket_name:
                raise ValueError("Bucket name is required")
                
            os.makedirs(local_path, exist_ok=True)
            
            if key == '':  
                all_files = self.list_all_files(bucket_name)
                for file in all_files:
                    file_key = file['key']
                    relative_path = os.path.join(local_path, file_key)
                    os.makedirs(os.path.dirname(relative_path), exist_ok=True)
                    
                    self.s3.download_file(bucket_name, file_key, relative_path)
                    logger.info(f"Downloaded {file_key} to {relative_path}")
            else:
                local_file_path = os.path.join(local_path, os.path.basename(key))
                self.s3.download_file(bucket_name, key, local_file_path)
                logger.info(f"Downloaded {key} to {local_file_path}")
                    
        except Exception as e:
            logger.info(f"Error downloading file(s) from bucket {bucket_name}: {str(e)}")

