from fastapi import APIRouter
import requests
import os
from gtts import gTTS
from dotenv import load_dotenv
import os
from model import ImageInput
import cv2
import numpy as np
import base64
import io
from PIL import Image, ExifTags

load_dotenv()

API_KEY = os.environ.get("API_KEY")

fileName = 1


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)


# # 원본 파일을 다양한 속도로 변환하는 함수
# def speedup_tts(original_filename, output_filename, speed):
#     sound = AudioSegment.from_file(original_filename, format="mp3")
#     sound_with_speed = sound.speedup(playback_speed=speed)
#     sound_with_speed.export(output_filename, format="mp3")


# base64 문자열을 이미지로 변환하는 함수
def base64_to_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(img_data))
        # 촬영한 이미지는 EXIF 정보로 정위값을 잡음, 이를 무시하면 회전된 사진을 다루게 되므로 이를 기준으로 회전시키는 코드
        if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    e = exif.get(orientation, 1)
                    if e == 3:
                        image = image.rotate(180, expand=True)
                    elif e == 6:
                        image = image.rotate(270, expand=True)
                    elif e == 8:
                        image = image.rotate(90, expand=True)
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding base64 string: {e}")
        raise


# 이미지를 base64로 변환하는 함수
def image_to_base64(image):
    _, buffer = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode("utf-8")


# 앞에 메타마크 떼는 함수
def clean_base64_string(base64_string: str) -> str:
    parts = base64_string.split(",", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return base64_string


# 릴루미노 모드 (저시력)
def relumino_mode(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    equalized = cv2.equalizeHist(blurred)
    adaptive_thresh = cv2.adaptiveThreshold(
        equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    mask = adaptive_thresh == 255
    output_image = np.zeros_like(image)
    output_image[mask] = [0, 0, 0]
    output_image[~mask] = image[~mask]
    return output_image


rgb2lms = np.array(
    [
        [0.31399022, 0.63951294, 0.04649755],
        [0.15537241, 0.75789446, 0.08670142],
        [0.01775239, 0.10944209, 0.87256922],
    ]
)
lms_deuteranopia = np.array([[1, 0, 0], [0.494207, 0, 1.24827], [0, 0, 1]])
lms2rgb = np.linalg.inv(rgb2lms)


def rgb_to_lms(rgb):
    return np.dot(rgb, rgb2lms.T)


def simulate_deuteranopia(lms):
    return np.dot(lms, lms_deuteranopia.T)


def lms_to_rgb(lms):
    return np.dot(lms, lms2rgb.T)


def daltonize(image):
    lms_image = rgb_to_lms(image)
    lms_deuter_image = simulate_deuteranopia(lms_image)
    deuter_image = lms_to_rgb(lms_deuter_image)
    error = image - deuter_image
    corrected_image = image + error * 0.2
    return np.clip(corrected_image, 0, 1)


# 적록색맹
def process_image_base64(encoded_image) -> str:
    image = base64_to_image(encoded_image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) / 255.0
    corrected_image = daltonize(image)
    corrected_image_bgr = (corrected_image * 255).astype(np.uint8)
    encoded_corrected_image = image_to_base64(corrected_image_bgr)
    return encoded_corrected_image


# 전색맹
def gray_scale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    equalized = cv2.equalizeHist(blurred)
    adaptive_thresh = cv2.adaptiveThreshold(
        equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    output_image = np.zeros_like(image)
    output_image[:, :, 0] = gray
    output_image[:, :, 1] = gray
    output_image[:, :, 2] = gray
    mask = adaptive_thresh == 255
    output_image[mask] = [0, 0, 0]
    output_image[~mask] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)[~mask]
    return output_image


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
            imgBase64 = ""
            if imageInput.displayMode == "general":
                imgBase64 = imageInput.image

            elif imageInput.displayMode == "lowVision":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                img = base64_to_image(cleanedBase64)
                adj = relumino_mode(img)
                imgBase64 = metaTag + "," + image_to_base64(adj)

            elif imageInput.displayMode == "redGreenColorBlind":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                imgBase64 = metaTag + "," + process_image_base64(cleanedBase64)

            elif imageInput.displayMode == "totallyColorBlind":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                img = base64_to_image(cleanedBase64)
                adj = gray_scale(img)
                imgBase64 = metaTag + "," + image_to_base64(adj)

            content = response.json()["choices"][0]["message"]["content"]
            text_to_speech(content, f"./mp3/{fileName}.mp3")
            return {"msg": content, "mp3": f"/mp3/{fileName}", "image": imgBase64}
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
            text_to_speech(content, f"./mp3/image/{fileName}.mp3")
            # speedup_tts(
            #     f"./mp3/image/{fileName}.mp3",
            #     f"./mp3/image/{fileName}.mp3",
            #     float(imageInput.ttsSpeed),
            # )
            return {"msg": content, "mp3": f"/mp3/image/{fileName}"}
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
            imgBase64 = ""
            if imageInput.displayMode == "general":
                imgBase64 = imageInput.image

            elif imageInput.displayMode == "lowVision":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                img = base64_to_image(cleanedBase64)
                adj = relumino_mode(img)
                imgBase64 = metaTag + "," + image_to_base64(adj)

            elif imageInput.displayMode == "redGreenColorBlind":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                imgBase64 = metaTag + "," + process_image_base64(cleanedBase64)

            elif imageInput.displayMode == "totallyColorBlind":
                metaTag, cleanedBase64 = clean_base64_string(imageInput.image)
                img = base64_to_image(cleanedBase64)
                adj = gray_scale(img)
                imgBase64 = metaTag + "," + image_to_base64(adj)

            content = response.json()["choices"][0]["message"]["content"]
            text_to_speech(content, f"./mp3/{fileName}.mp3")
            return {"msg": content, "mp3": f"/mp3/{fileName}", "image": imgBase64}
        except KeyError as e:
            return {"msg": e, "mp3": ""}
