import base64
import requests
import os
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from gtts import gTTS
from dotenv import load_dotenv
import os

API_KEY = os.environ.get("API_KEY")


# 이미지를 base64로 인코딩하는 함수
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def text_to_speech(text, filename):
    """gTTS를 사용하여 텍스트를 음성으로 변환합니다."""
    tts = gTTS(text=text, lang="ko")
    tts.save(filename)
    os.system(f"mpg321 {filename}")


# 이미지 경로
image_path = "./triangle.png"

# base64 문자열 얻기
base64_image = encode_image(image_path)

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

payload = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "이 사진에 대해 설명해줘"},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            ],
        },
    ],
    "max_tokens": 1000,
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
)

# 응답 오류 처리
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.json())
else:
    try:
        content = response.json()["choices"][0]["message"]["content"]
        text_to_speech(content, "response.mp3")
        # 응답 출력
        print(content)
    except KeyError as e:
        print(f"KeyError: {e}")
        print(response.json())

# 이미지 표시
img = Image.open(image_path)
plt.imshow(img)
plt.axis("off")
plt.show()
