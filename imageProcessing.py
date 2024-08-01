import cv2
import numpy as np
import base64
import io
from PIL import Image

# base64 문자열을 이미지로 변환하는 함수
def base64_to_image(base64_string):
    img_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(img_data))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# 릴루미노 모드를 적용하는 함수
def relumino_mode(image):
    # 이미지를 그레이스케일로 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 블러 적용하여 노이즈 감소
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 히스토그램 평활화 적용
    equalized = cv2.equalizeHist(blurred)

    # 적응형 임계값 적용
    adaptive_thresh = cv2.adaptiveThreshold(equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 흰색 부분을 검정색으로, 검정색 부분을 원본 이미지로 변경
    mask = adaptive_thresh == 255
    output_image = np.zeros_like(image)
    output_image[mask] = [0, 0, 0]
    output_image[~mask] = image[~mask]

    return output_image

# base64 문자열 예시 (위의 이미지 인코딩 예제에서 생성된 문자열 사용)
encoded_image = base64_image

# base64 문자열을 이미지로 변환
image = base64_to_image(encoded_image)

# 릴루미노 모드 적용
adjusted_image = relumino_mode(image)

# 결과 출력
cv2_imshow(adjusted_image)
+++++++++++++++++++++++++++++
# RGB to LMS 변환 매트릭스
rgb2lms = np.array([[0.31399022, 0.63951294, 0.04649755],
                    [0.15537241, 0.75789446, 0.08670142],
                    [0.01775239, 0.10944209, 0.87256922]])

# 적록색맹을 위한 LMS 보정 매트릭스
lms_deuteranopia = np.array([[1, 0, 0],
                             [0.494207, 0, 1.24827],
                             [0, 0, 1]])

# LMS to RGB 변환 매트릭스
lms2rgb = np.linalg.inv(rgb2lms)

def rgb_to_lms(rgb):
    return np.dot(rgb, rgb2lms.T)

def simulate_deuteranopia(lms):
    return np.dot(lms, lms_deuteranopia.T)

def lms_to_rgb(lms):
    return np.dot(lms, lms2rgb.T)

def daltonize(image):
    # 이미지의 RGB 값을 LMS로 변환
    lms_image = rgb_to_lms(image)

    # 적록색맹 시뮬레이션
    lms_deuter_image = simulate_deuteranopia(lms_image)

    # 적록색맹 시뮬레이션 이미지를 다시 RGB로 변환
    deuter_image = lms_to_rgb(lms_deuter_image)

    # 원본 이미지와 시뮬레이션 이미지의 차이 계산
    error = image - deuter_image

    # 오류를 보정하여 새로운 이미지 생성
    corrected_image = image + error * 0.2  # 보정 강도 조절 가능

    return np.clip(corrected_image, 0, 1)  # 값 범위 조정


def process_image_base64(encoded_image):
    # base64 문자열을 이미지로 변환
    image = base64_to_image(encoded_image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) / 255.0  # RGB로 변환하고 정규화

    # 색상 보정
    corrected_image = daltonize(image)

    # 보정된 이미지를 base64 문자열로 변환
    corrected_image_bgr = (corrected_image * 255).astype(np.uint8)
    encoded_corrected_image = image_to_base64(corrected_image_bgr)

    return encoded_corrected_image

# 예시 base64 문자열 (여기서는 실제로 사용할 base64 문자열을 넣어야 합니다)
encoded_image = base64_image

# 이미지 처리 및 보정
encoded_corrected_image = process_image_base64(encoded_image)

# 보정된 이미지 출력
corrected_image = base64_to_image(encoded_corrected_image)

cv2_imshow(corrected_image)
++++++++++++++++++++++++++++
def gray_scale(image):
    # 이미지를 그레이스케일로 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 블러 적용하여 노이즈 감소
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 히스토그램 평활화 적용
    equalized = cv2.equalizeHist(blurred)

    # 적응형 임계값 적용
    adaptive_thresh = cv2.adaptiveThreshold(equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 흰색 부분을 그레이스케일 이미지와 합치기
    output_image = np.zeros_like(image)
    output_image[:, :, 0] = gray  # 그레이스케일 이미지를 각 채널에 할당
    output_image[:, :, 1] = gray
    output_image[:, :, 2] = gray

    # 흰색 부분을 그레이스케일 이미지로, 검정색 부분을 검정색으로 설정
    mask = adaptive_thresh == 255
    output_image[mask] = [0, 0, 0]
    output_image[~mask] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)[~mask]

    return output_image

def process_image_base64(encoded_image):
    # base64 문자열을 이미지로 변환
    image = base64_to_image(encoded_image)

    # 그레이스케일 변환 적용
    output_image = gray_scale(image)

    # 결과 이미지를 base64 문자열로 변환
    encoded_output_image = image_to_base64(output_image)

    return encoded_output_image

# 예시 base64 문자열 (여기서는 실제로 사용할 base64 문자열을 넣어야 합니다)
encoded_image = encoded_image

# 이미지 처리
encoded_output_image = process_image_base64(encoded_image)

# 결과 이미지 시각화 (디코딩하여 보여줌)
output_image = base64_to_image(encoded_output_image)

cv2_imshow(output_image)