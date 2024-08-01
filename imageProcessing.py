import cv2
import numpy as np


class ImageProcessing:
    def relumino_mode(image_path):
        # 이미지 읽기
        image = cv2.imread(image_path)
        # 이미지를 그레이스케일로 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 블러 적용하여 노이즈 감소
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # 히스토그램 평활화 적용
        equalized = cv2.equalizeHist(blurred)
        # 적응형 임계값 적용
        adaptive_thresh = cv2.adaptiveThreshold(
            equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        # 흰색 부분을 검정색으로, 검정색 부분을 원본 이미지로 변경
        mask = adaptive_thresh == 255
        output_image = np.zeros_like(image)
        output_image[mask] = [0, 0, 0]
        output_image[~mask] = image[~mask]
        return output_image
