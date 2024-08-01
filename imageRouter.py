from fastapi import APIRouter
import requests
import os
from gtts import gTTS
from dotenv import load_dotenv
import os
from model import ImageInput
from pydub import AudioSegment


load_dotenv()

API_KEY = os.environ.get("API_KEY")

fileName = 1


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)


# 원본 파일을 다양한 속도로 변환하는 함수
def speedup_tts(original_filename, output_filename, speed):
    sound = AudioSegment.from_file(original_filename, format="mp3")
    sound_with_speed = sound.speedup(playback_speed=speed)
    sound_with_speed.export(output_filename, format="mp3")


headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}


"""FAST API"""
imageRouter = APIRouter()


# 카메라 촬영 이미지
@imageRouter.post("/cameraimage")
async def postCameraImage(imageInput: ImageInput) -> dict:
    global fileName
    fileName += 1
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "시각장애인에게 이 사진에 대해 100자 이내로 너가 앞이 안 보인다고 생각하고 존댓말로 설명해줘.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": imageInput.image},
                    }
                ],
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
            speedup_tts(
                f"./mp3/{fileName}.mp3",
                f"./mp3/{fileName * 10}.mp3",
                float(imageInput.ttsSpeed),
            )
            return {"msg": content, "mp3": f"/mp3/{fileName * 10}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}


# 전맹 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/totallyblind")
async def postWebviewTotallyBlind(imageInput: ImageInput) -> dict:
    global fileName
    fileName += 1
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "답변을 받는 사람은 전맹 시각 장애가 있어. 사진에 대해 100자 이내로 대화하듯 존댓말로 설명해줘",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": imageInput.image},
                    }
                ],
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
            speedup_tts(
                f"./mp3/{fileName}.mp3",
                f"./mp3/{fileName}.mp3",
                float(imageInput.ttsSpeed),
            )
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}


# 저시력 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/lowvision")
async def postWebviewLowVision(imageInput: ImageInput) -> dict:
    global fileName
    fileName += 1
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "답변을 받는 사람은 저시력 장애가 있어. 사진에 대해 100자 이내로 대화하듯 존댓말로 설명해줘",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": imageInput.image},
                    }
                ],
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
            speedup_tts(
                f"./mp3/{fileName}.mp3",
                f"./mp3/{fileName}.mp3",
                float(imageInput.ttsSpeed),
            )
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}
