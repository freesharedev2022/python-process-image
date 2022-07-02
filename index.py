#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qrcode
import requests
import os
import os.path
import random
from dotenv import load_dotenv
from PIL import Image,  ImageDraw, ImageFont, ImageFilter
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_url_path='')
load_dotenv()
CORS(app)

def gen_qrcode(qrText=''):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(qrText)
    qr.make(fit=True)
    img = qr.make_image()
    small_img = img.resize((350, 350), Image.ANTIALIAS)
    small_img.save("./cards/qrcode.png")


def format_email(email):
    email = email.split('@')
    text1 = email[0][:2]
    position = email[1].find('.')
    extention = email[1][position::]
    text2 = email[1][:1] + '**' + extention
    return text1 + '**' + '@' + text2


def mask_circle_transparent(pil_img, blur_radius, offset=0):
    try:
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        result = pil_img.copy()
        result.putalpha(mask)
        return result
    except Exception as e:
        print(e)
        pass


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, max(pil_img.size), max(pil_img.size))


def crop_min_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def download_image(image_url='', folder='./avatar/avatar.png'):
    try:
        img_data = requests.get(image_url).content
        with open(folder, 'wb') as handler:
            handler.write(img_data)
        return 'ok'
    except Exception as e:
        print(e)
        return 'error'


def drawImage(id, name, email, avatar):
    try:
        rand = random.randint(1, 5)
        main_color = getMainColor(rand)

        # xử lý resize và lưu lại ảnh mới, dùng trong trường hợp kích thước ảnh khác nhau
        im = Image.open('./avatar/' + avatar)
        im_square = crop_min_square(im).resize((241, 241), Image.LANCZOS)
        im_thumb = mask_circle_transparent(im_square, 2)
        im_thumb.save('./avatar/avatar_resize_default.png')

        back_ground = './cards/card-demo.jpeg'

        qr_text = 'Test-' + id
        gen_qrcode(qr_text)
        background = Image.open(back_ground, 'r')

        avatar = Image.open('./avatar/avatar_resize_default.png', 'r')
        qrcode = Image.open('./cards/qrcode.png', 'r')

        text_img = background.copy()

        text_img.paste(avatar, (392, 270))
        text_img.paste(qrcode, (350, 610))

        fntBold = ImageFont.truetype('./fonts/Roboto-Bold.ttf', 52, encoding="utf-8")
        fntBlack = ImageFont.truetype('./fonts/Roboto-Bold.ttf', 75, encoding="utf-8")
        fntEmail = ImageFont.truetype('./fonts/Roboto-Bold.ttf', 32, encoding="utf-8")
        draw = ImageDraw.Draw(text_img)

        name_padding = 280
        draw.text((name_padding, 100), name, font=fntBlack, fill=main_color)

        id_padding = 450
        draw.text((id_padding, 200), "ID-" + id, font=fntBold, fill=main_color)

        f_email = format_email(email)
        f_email_padding = 400
        draw.text((f_email_padding, 550), f_email, font=fntEmail, fill=main_color)

        text_img.save('./test-image/' + id + '.png', format="png")

    except Exception as e:
        print(e)
        pass

def getMainColor(argument):
    switcher = {
        1: (230, 73, 84),
        2: (72, 59, 142),
        3: (59, 181, 223),
        4: (245, 142, 35),
        5: (64, 140, 71)
    }
    return switcher.get(argument, "Invalid")


def randomData(argument):
    switcher = {
        1: (1, 'Nguyễn Văn A', 'nguyenvana@gmail.com','avatar.png'),
        2: (2, 'Nguyễn Văn B', 'nguyenvanb@gmail.com','avatar.png'),
        3: (3, 'Nguyễn Văn B', 'nguyenvanc@gmail.com', 'avatar.png'),
        4: (4, 'Trần Văn A', 'tranvana@gmail.com', 'avatar.png'),
        5: (5, 'Trần Văn B', 'tranvanb@gmail.com', 'avatar.png')
    }
    return switcher.get(argument, "Invalid")

def process_image(name):
    try:
        rand = random.randint(1,5)
        print(rand)
        data = randomData(rand)
        print("Variable %s, %s, %s, %s" %(data[0], data[1], data[2], data[3]))
        drawImage(str(name), str(data[1]), str(data[2]), str(data[3]))
        return 'ok'
    except Exception as e:
        print("Error get cards : %s", e)
        return 'Error execute'

@app.route('/')
def home():
    return "Success !"

@app.route('/test-image/<path>')
def check_image(path):
    if '.png' not in path:
        return 'Invalid url'
    check = os.path.exists('./test-image/' + path)
    path = path.lower()
    name = path.replace('.png', '')
    if check:
        return send_from_directory('test-image', path)
    else:
        result_path = process_image(name)
        if result_path == 'ok':
            return send_from_directory('test-image', path)
        return result_path
    return 'Error'


if __name__ == '__main__':
    app.run(port=8000)