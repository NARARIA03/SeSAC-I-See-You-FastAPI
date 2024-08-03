from fastapi import APIRouter
import requests
from gtts import gTTS
from model import VoiceInput


fileName = 1


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)


"""FAST API"""
voiceRouter = APIRouter()


@voiceRouter.post("/voice")
async def postCameraImage(voiceInput: VoiceInput) -> dict:
    global fileName
    try:
        content = "정상적으로 요청이 완료되었어요."
        return {"msg": content, "mp3": f"/mp3/{fileName}"}
    except KeyError as e:
        return {"msg": e, "mp3": ""}
