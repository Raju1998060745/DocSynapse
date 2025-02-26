import logging
from service_1.providers.aws_provider import AWSProvider

from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,  # or DEBUG, WARNING, ERROR, etc.
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),    # writes logs to a file named app.log
        logging.StreamHandler()            # prints logs to console
    ]
)


load_dotenv()



dnd= AWSProvider()

dnd.list_all_files(os.getenv('AWS_BUCKET_NAME'))


dnd.download_files(os.getenv('AWS_BUCKET_NAME'))