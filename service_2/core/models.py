from pydantic import BaseModel

class FileUploadRequest(BaseModel):
    filename: list[str]
    user: str
    fileDirectory: str | None = None
    
class RagRequestModel(BaseModel):
    user: str
    query: str
    document_name: str | None = None