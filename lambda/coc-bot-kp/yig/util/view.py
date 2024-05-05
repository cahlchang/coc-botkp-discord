import requests
import json
import boto3
import os
import math
import gzip
from PIL import Image, ImageDraw, ImageFont

import yig.config


def write_pc_image(guild_id, user_id, pc_id, image_byte):
    image_key = f"{guild_id}/{user_id}/{pc_id}_thum.jpg"
    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=yig.config.AWS_S3_BUCKET_NAME,
        Key=image_key,
        Body=image_byte,
        Tagging="public-object=yes",
        ContentType="image/jpeg",
    )

    return image_key


def get_pc_image_url(guild_id, user_id, pc_id, ts) -> str:
    print("pc image called")
    url = f"https://d2ictenzfe6sat.cloudfront.net/{guild_id}/{user_id}/{pc_id}_thum.jpg?{ts}"
    response = requests.head(url)
    print(response.status_code)
    if response.status_code == 403:
        return "https://d13xcuicr0q687.cloudfront.net/public/noimage.jpg"
    else:
        return url
