import cv2
import pytesseract
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import re
import sys


def remove_false_text(text) -> str:
    remove_line_break = text.replace("\n", " ")[:-1]
    cleaned_text = re.sub(r"^[^a-zA-Z0-9]*|[^a-zA-Z0-9\)]*$", "", remove_line_break)
    return cleaned_text


def get_card(type: str, url: str) -> list[str]:

    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image_array = np.array(image)

    if type == "character":
        # CARD NAME COORDINATE
        start_y = 60
        end_y = 105

    elif type == "anime":
        # CARD ANIME COORDINATE
        start_y = 310
        end_y = 360

    # FIRST CARD ONLY
    card1_x = 55
    card1_w = 240

    # SECOND CARD ONLY
    card2_x = 325
    card2_w = 515

    # THIRD CARD ONLY
    card3_x = 605
    card3_w = 785


    card1 = image_array[start_y:end_y, card1_x:card1_w]
    card2 = image_array[start_y:end_y, card2_x:card2_w]
    card3 = image_array[start_y:end_y, card3_x:card3_w]
    cards = [card1, card2, card3]
    
    result = []

    for card in cards:
        #Preprocessing image
        #Converting to grayscale
        gray_image = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
        
        #creating Binary image by selecting proper threshold
        binary_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        #Inverting the image
        inverted_bin = cv2.bitwise_not(binary_image)
        
        #Some noise reduction
        kernel = np.ones((2,2),np.uint8)
        processed_img = cv2.erode(inverted_bin, kernel, iterations = 1)
        processed_img = cv2.dilate(processed_img, kernel, iterations = 1)

        text = pytesseract.image_to_string(processed_img, config = "--psm 6")
        anime_name = remove_false_text(text)
        result.append(anime_name)

    print(result)
    return result

if __name__  == "__main__":
    get_card("anime", sys.argv[1])