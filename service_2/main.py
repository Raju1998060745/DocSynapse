from fastapi import FastAPI

from .utils.document_utils import load_and_split_documents
app = FastAPI()



@app.get("/home")
async def index():
   return {"message": "Hello Worldhi "}


@app.get("/load")
async def index(uuid : str , file_loc : str = None):
   return load_and_split_documents(file_loc)