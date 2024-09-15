import requests
import json
import boto3
import os
import math
import gzip
from PIL import Image, ImageDraw, ImageFont

import yig.config


def write_pc_image(guild_id, user_id, pc_id, image_bytes):
    image_key = f"{guild_id}/{user_id}/{pc_id}_thum.jpg"
    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=yig.config.AWS_S3_BUCKET_NAME,
        Key=image_key,
        Body=image_bytes,
        Tagging="public-object=yes",
        ContentType="image/jpeg",
    )

    return image_key

def write_pc_image_origin(guild_id, user_id, pc_id, image_bytes):
    image_key = f"{guild_id}/{user_id}/{pc_id}_origin.jpg"
    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=yig.config.AWS_S3_BUCKET_NAME,
        Key=image_key,
        Body=image_bytes,
        Tagging="public-object=yes",
        ContentType="image/jpeg",
    )

    return image_key


def get_pc_image_url(guild_id, user_id, pc_id, ts) -> str:
    url = f"https://d2ictenzfe6sat.cloudfront.net/{guild_id}/{user_id}/{pc_id}_thum.jpg?{ts}"
    response = requests.head(url)
    print(response.status_code)
    if response.status_code == 403:
        return "https://d13xcuicr0q687.cloudfront.net/public/noimage.jpg"
    else:
        return url

def create_param_image(user_param):
    # math define
    n = 8
    W = H = 400
    r = 200
    radian = 2 * math.pi / n
    w = h = 0
    h_o = 5

    # color define
    white = (255, 255, 255)
    black = (0, 0, 0)
    dimgray = (105, 105, 105)
    gray = (127, 135, 143)
    light_sky_blue = (180, 235, 250)

    textsize = 48
    font = ImageFont.truetype("font/04Takibi-Medium.otf", textsize)
    lst_param_name = ["STR", "CON", "POW", "DEX", "APP", "SIZ", "INT", "EDU"]

    canvas = Image.new('RGB', (W, H), white)
    draw = ImageDraw.Draw(canvas)
    lst_coord =[]
    for i in range(0, 9):
        cood = (math.cos(i*radian)*r+W/2,
                math.sin(i*radian)*r+H/2)
        lst_coord.append(cood)

    draw.line(lst_coord,
            fill=black,
            width=3)
    if user_param["game"] == "coc":
        params = [
            float(user_param['POW'])/18,
            float(user_param['DEX'])/18,
            float(user_param['APP'])/18,
            float(user_param['SIZ'])/18,
            float(user_param['INT'])/18,
            float(user_param['EDU'])/21,
            float(user_param['STR'])/18,
            float(user_param['CON'])/18
        ]
    elif user_param["game"] == "coc7":
        params = [
            float(user_param['POW'])/100,
            float(user_param['DEX'])/100,
            float(user_param['APP'])/100,
            float(user_param['SIZ'])/100,
            float(user_param['INT'])/100,
            float(user_param['EDU'])/100,
            float(user_param['STR'])/100,
            float(user_param['CON'])/100
        ]

    lst_param_cood = []
    for i in range(0, 8):
        param_cood = (
            math.cos(i*radian)*r*params[i]+W/2,
            math.sin(i*radian)*r*params[i]+H/2
        )
        lst_param_cood.append(param_cood)

    draw.polygon(
        lst_param_cood,
        outline=black,
        fill=light_sky_blue
    )

    def get_point(w, h, i):
        yield [
            ((W-w)/2, h_o),
            (W-w-h_o, h_o*7),
            (W-w, H/2-h/2),
            (W-w-h_o, H-h_o*7-h),
            ((W-w)/2, H-h-h_o),
            (h_o, H-h_o*7-h),
            (0, (H-h)/2),
            (h_o*1, h_o*7),
            ((W-w)/2, h_o)
        ][i]

    for i, name in enumerate(lst_param_name):
        w = draw.textlength(name, font=font)
        h = textsize
        draw.text(
            next(get_point(w, h, i)),
            name,
            dimgray,
            font=font
        )

    lst_auxiliary_line = [
        [(W/2, 0), (W/2, H)],[(0, H/2), (W, H/2)],
        [(math.cos(1*radian)*r+W/2, math.sin(1*radian)*r+H/2),
        (math.cos(5*radian)*r+W/2, math.sin(5*radian)*r+H/2)],
        [(math.cos(3*radian)*r+W/2, math.sin(3*radian)*r+H/2),
        (math.cos(7*radian)*r+W/2, math.sin(7*radian)*r+H/2)]
    ]

    for auxiliary_line in lst_auxiliary_line:
        draw.line(
            auxiliary_line,
            fill=gray,
            width=1
        )

    lst_inner_line = []
    for j in [1/3, 2/3]:
        lst_each = []
        for i in range(0,9):
            lst_each.append(
                (math.cos(i*radian)*r*j+W/2,
                math.sin(i*radian)*r*j+H/2)
            )
        lst_inner_line.append(lst_each)

    for inner_line in lst_inner_line:
        draw.line(
            inner_line,
            fill=gray,
            width=1
        )
    return canvas

def save_param_image(image, guild_id, user_id, pc_id):
    image_param_path = f"/tmp/{pc_id}_param.png"
    image_param_key = f"{guild_id}/{user_id}/{pc_id}_param.png"
    image.save(image_param_path)

    s3_client = boto3.client('s3')
    s3_client.upload_file(image_param_path, yig.config.AWS_S3_BUCKET_NAME, image_param_key)
    s3_client.put_object_tagging(
        Bucket = yig.config.AWS_S3_BUCKET_NAME,
        Key = image_param_key,
        Tagging = {'TagSet': [ { 'Key': 'public-object', 'Value': 'yes' }, ]})

    return f"https://d2ictenzfe6sat.cloudfront.net/{guild_id}/{user_id}/{pc_id}_param.png"
