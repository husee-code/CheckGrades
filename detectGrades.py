import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'D:\\py_projects\\TESSERACT\\tesseract.exe'


def enhance(img: Image) -> Image:
    enhancer = ImageEnhance.Sharpness(img)
    factor = 0  # чем меньше, тем больше резкость
    return enhancer.enhance(factor)


def contraharmonic_mean(img: Image, size, Q) -> Image:
    img = np.array(img)
    num = np.power(img, Q + 1)
    denom = np.power(img, Q)
    kernel = np.full(size, 1.0)
    result = cv2.filter2D(num, -1, kernel) / cv2.filter2D(denom, -1, kernel)
    return Image.fromarray(np.uint8(result))


def is_black(pixel: tuple) -> bool:
    return not ((pixel[0] > 20) or (pixel[1] > 20) or (pixel[2] > 20))


def is_white(pixel: tuple) -> bool:
    return pixel[0] > 160 and pixel[1] > 160 and pixel[2] > 160


def white_or_black(pixel: tuple) -> bool:
    return is_black(pixel) or is_white(pixel)


def remain_black_pixels(img: Image) -> Image:
    width, height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            if pixel[0] > 100 or pixel[1] > 100 or pixel[2] > 100:
                pixels[x, y] = (255, 255, 255, 255)
    return img


def check_theme(img: Image) -> str:
    width, height = img.size
    pixels = img.load()
    white_count = 0
    black_count = 0
    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            if is_white(pixel):
                white_count += 1
            elif is_black(pixel):
                black_count += 1

    if white_count > black_count:
        return 'WHITE'
    return 'BLACK'


def black_to_clear_white(img: Image) -> Image:
    width, height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            pixel = pixels[x, y]
            if not is_white(pixel):
                pixels[x, y] = (255, 255, 255, 255)
            else:
                pixels[x, y] = (0, 0, 0, 255)
    return img


def clear_from_1(array: list) -> list:
    result = []
    for i in array:
        for j in i.split():
            if j != '1':
                result.append(j)
    return result


def average(grades) -> float:
    grades = list(map(int, grades))
    return sum(grades) / len(grades)


def detect_grades(img: Image) -> list:
    if check_theme(img) == 'BLACK':
        img = contraharmonic_mean(img, (3, 3), 0.5)
        img = black_to_clear_white(img)
        img = enhance(img)
        # gotcha!

    else:
        img = remain_black_pixels(img)
        img = contraharmonic_mean(img, (3, 3), 0.5)
        img = enhance(img)
        # gotcha!

    grades = pytesseract.image_to_string(
        img,
        config='--psm 6 -c tessedit_char_whitelist=12345').split('\n')
    return clear_from_1(grades)


# ТЕСТЫ
if __name__ == '__main__':
    """image = Image.open('test_data\\m_black.jpg')
    grades_ = detect_grades(image)
    print(grades_)
    print(average(grades_))"""
    image = Image.open('test_data\\m_black.jpg')
    print(np.array(image))

