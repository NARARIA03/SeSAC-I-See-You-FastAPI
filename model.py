from pydantic import BaseModel


class ImageInput(BaseModel):
    image: str
