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


# 이미지를 base64로 인코딩하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


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
            {"role": "user", "content": "이 사진에 대해 설명해줘"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": imageInput.image},  # base64 문자열 사용
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
            # 응답 출력
            print(content)
            return {"msg": content, "mp3": f"/mp3/{fileName}"}
        except KeyError as e:
            return {"msg": e, "mp3": ""}


# 전맹 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/totallyblind")
async def postWebviewTotallyBlind() -> dict:
    return {}


# 저시력 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/lowvision")
async def postWebviewLowVision() -> dict:
    return {}
