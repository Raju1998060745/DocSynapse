import logging
from service.providers.aws_provider import AWSProvider
from service.utils.db_connect import DatabaseConnect
from datetime import datetime, timezone
from dotenv import load_dotenv, set_key ,find_dotenv
from zoneinfo import ZoneInfo


import os
from service.utils.logger_utils import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)    
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


dbConnect = DatabaseConnect()
dnd= AWSProvider()



previous_files = dbConnect.get_all_s3_objects()
latest_files = dnd.list_all_files(AWS_BUCKET_NAME)

files =dnd.compare_files(previous_files)


for file in files:
    logger.debug(f"Processing file: {file['key']}")
    if file['is_modified']:
        dnd.download_files(AWS_BUCKET_NAME, file['key'])
        logger.info(f"Downloaded {file['key']} to {os.getenv('FILE_DOWNLOAD_PATH')}")
    else:
        logger.info(f"File {file['key']} is not modified, skipping download.")

dbConnect.store_s3_objects_info(latest_files)


# set_key(
#     find_dotenv(),
#     "LAST_SCAN_TIME",
#     f"{datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')}"
# )

