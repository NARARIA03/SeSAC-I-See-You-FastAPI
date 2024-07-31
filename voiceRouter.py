from fastapi import APIRouter
import requests
import os
from gtts import gTTS
from dotenv import load_dotenv
import os
from model import VoiceInput

load_dotenv()

API_KEY = os.environ.get("API_KEY")

fileName = 1


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)
    os.system(f"mpg321 {filename}")


headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}


"""FAST API"""
voiceRouter = APIRouter()


@voiceRouter.post("/voice")
async def postVoice(voiceInput: VoiceInput) -> dict:
    global fileName
    fileName += 1
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": f"저번 답변은 {voiceInput.prevText}이거였어. 그리고 지금 질문은 '{voiceInput.reqText}'야 이 질문에 대해 답변해줘.",
            },
        ],
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    if response.status_code != 200:
        return {"msg": response.status_code, "mp3": ""}
    else:
        try:
            content = response.json()["choices"][0]["message"]["content"]
            text_to_speech(content, f"./mp3/{fileName}.mp3")
            # 응답 출력
            print(content)
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}
