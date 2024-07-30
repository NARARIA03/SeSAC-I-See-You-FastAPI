from fastapi import APIRouter
import base64
import requests
import os
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from gtts import gTTS
from dotenv import load_dotenv
import os
from model import ImageInput

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
                "content": "시각장애인에게 이 사진에 대해 100자 이내로 설명해줘. 어떤 위치에 어떤 물체가 있는지, 무엇을 조심해야하는지에 중점을 두고 설명해줘.",
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
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
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
                "content": "사진에 대해 200자 이내로 설명해줘.",
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
                "content": "사진에 대해 200자 이내로 설명해줘.",
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
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}
