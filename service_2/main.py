from fastapi import FastAPI

from service_2.utils.document_utils import load_and_split_documents
app = FastAPI()

load_and_split_documents('')


@app.get("/home")
async def index():
   return {"message": "Hello Worldhi "}


@app.get("/testload")
async def index():
   return load_and_split_documents('')

@app.get("/load")
async def index(uuid : str , file_loc : str = None):
   return load_and_split_documents(file_loc)