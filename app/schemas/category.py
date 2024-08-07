from pydantic import BaseModel

class CategorySchema(BaseModel):
    name: str

    class Config:
        from_attributes = True