import boto3
from data import load_documents, split_documents, get_documents_list
from datastore import store_s3_objects_info

# Use profile_name correctly within Session, not in client()

store_s3_objects_info()



# documents = load_documents()

# chunks = split_documents(documents)

# print(chunks[0])