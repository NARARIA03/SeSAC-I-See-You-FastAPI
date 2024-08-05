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
    fileName += 1
    try:
        content = f"voice 엔드포인트 정상 응답 완료 {fileName}"
        text_to_speech(content, f"./mp3/{fileName}.mp3")
        return {"msg": content, "mp3": f"/mp3/{fileName}"}
    except KeyError as e:
        return {"msg": e, "mp3": ""}
