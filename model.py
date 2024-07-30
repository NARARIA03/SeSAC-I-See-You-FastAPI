from pydantic import BaseModel


class ImageInput(BaseModel):
    image: str


class VoiceInput(BaseModel):
    reqText: str
    prevText: str
