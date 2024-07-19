from pydantic import BaseModel, ValidationError, constr, conint


class NoteSchema(BaseModel):
    title: constr(max_length=100)
    content: str
    user_id: conint(gt=0)
    category_id: conint(gt=0) = None

    class Config:
        from_attributes = True