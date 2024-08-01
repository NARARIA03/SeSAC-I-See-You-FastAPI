from pydantic import BaseModel
from typing import Literal


class ImageInput(BaseModel):
    image: str
    displayMode: Literal[
        "general",
        "lowVision",
        "totallyBlind",
        "redGreenColorBlind",
        "totallyColorBlind",
    ]
    ttsSpeed: Literal["1.0", "1.25", "1.5", "1.75", "2.0"]


class VoiceInput(BaseModel):
    reqText: str
    prevText: str
    prevImage: str
    displayMode: Literal[
        "general",
        "lowVision",
        "totallyBlind",
        "redGreenColorBlind",
        "totallyColorBlind",
    ]
    ttsSpeed: Literal["1.0", "1.25", "1.5", "1.75", "2.0"]
