from fastapi import APIRouter
from gtts import gTTS
from model import ImageInput
import cv2
import numpy as np
import base64
import io
from PIL import Image


fileName = 1


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)


# base64 문자열을 이미지로 변환하는 함수
def base64_to_image(base64_string):
    try:
        img_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(img_data))
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


# 이미지 모드에 따라 변환해서 반환하는 함수
def return_new_image(imageInput: ImageInput) -> str:
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
    return imgBase64


"""FAST API"""
imageRouter = APIRouter()


# 카메라 촬영 이미지
@imageRouter.post("/cameraimage")
async def postCameraImage(imageInput: ImageInput) -> dict:
    global fileName
    try:
        imgBase64 = return_new_image(imageInput)
        content = "정상적으로 요청이 완료되었어요."
        return {"msg": content, "mp3": f"/mp3/{fileName}", "image": imgBase64}
    except KeyError as e:
        return {"msg": e, "mp3": "", "image": ""}


# 전맹 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/totallyblind")
async def postWebviewTotallyBlind(imageInput: ImageInput) -> dict:
    global fileName
    try:
        content = "정상적으로 요청이 완료되었어요."
        return {"msg": content, "mp3": f"/mp3/{fileName}"}
    except KeyError as e:
        return {"msg": e, "mp3": ""}


# 저시력 시각 장애인 웹뷰
@imageRouter.post("/webviewimage/lowvision")
async def postWebviewLowVision(imageInput: ImageInput) -> dict:
    global fileName
    try:
        imgBase64 = return_new_image(imageInput)
        content = "정상적으로 요청이 완료되었어요."
        return {"msg": content, "mp3": f"/mp3/{fileName}", "image": imgBase64}
    except KeyError as e:
        return {"msg": e, "mp3": "", "image": ""}
