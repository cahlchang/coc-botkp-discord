import numpy as np
import cv2
import requests
import datetime


from yig.bot import listener
from yig.util.data import (
    get_user_param,
    get_basic_status,
    build_user_panel,
    read_user_data
)
from yig.util.view import write_pc_image, get_pc_image_url, write_pc_image_origin
import yig.config


# @listener("change-status")
# def update_user_status(bot):
#     state_data = get_state_data(bot.team_id, bot.user_id)
#     user_param = get_user_param(bot.team_id, bot.user_id, state_data["pc_id"])
#     if "options" in bot.action_data and 2 == len(bot.action_data["options"]):
#         status_name, operator, arg = result
#         if status_name in state_data:
#             val_targ = state_data[status_name]
#         else:
#             val_targ = "0"

#    num_targ = eval(f'{val_targ}{operator}{arg}')
#    state_data[status_name] = num_targ
#    set_state_data(bot.team_id, bot.user_id, state_data)
#    return get_status_message("UPDATE STATUS", user_param, state_data), yig.config.COLOR_ATTENTION


@listener("status")
def show_status(bot):
    state_data = read_user_data(
        guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
    )
    user_param = get_user_param(
        guild_id=bot.guild_id, user_id=bot.user_id, pc_id=state_data["pc_id"]
    )
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
        user_param, state_data
    )
    image_url = get_pc_image_url(
        bot.guild_id, bot.user_id, state_data["pc_id"], state_data["ts"]
    )
    name = user_param["name"]
    title = "ステータス"
    field_name = ""
    field_value = ""
    # return build_detail_user_panel(title, field_name, field_value, yig.config.COLOR_INFO, name, now_hp, max_hp, now_mp, max_mp, now_san, max_san, db, image_url)
    return build_user_panel(
        title,
        field_name,
        field_value,
        yig.config.COLOR_INFO,
        name,
        now_hp,
        max_hp,
        now_mp,
        max_mp,
        now_san,
        max_san,
        db,
        image_url,
    )


@listener("addimage")
def add_character_image(bot)->dict:
    """character image

    Args:
        bot yig.Bot: Bot instance

    Raises:
        e: No face

    Returns:
        dict: return value
    """
    state_data = read_user_data(
        guild_id=bot.guild_id, user_id=bot.user_id, filename=yig.config.STATE_FILE_PATH
    )
    user_param = get_user_param(
        guild_id=bot.guild_id, user_id=bot.user_id, pc_id=state_data["pc_id"]
    )

    # Cascadeファイルの読み込み
    face_cascade_path = "xml/lbpcascade_animeface.xml"
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    image_url = bot.action_data["resolved"]["attachments"][
        bot.action_data["options"][0]["value"]
    ]["url"]
    response = requests.get(image_url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    write_pc_image_origin(
        guild_id=bot.guild_id,
        user_id=bot.user_id,
        pc_id=state_data["pc_id"],
        image_bytes=image.tobytes()
    )

    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 顔の検出
    try:
        face_rects = face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=5
        )
    except Exception as e:
        print(e)
        raise e

    # 検出された顔の領域から正方形を切り出し、リサイズする
    for x, y, w, h in face_rects:
        print("face find")
        # 顔の周りを取得する
        x1 = max(x - w // 2, 0)
        y1 = max(y - h // 2, 0)
        x2 = min(x + 3 * w // 2, image.shape[1])
        y2 = min(y + 3 * h // 2, image.shape[0])

        # 顔の周りを切り出す
        face_area = image[y1:y2, x1:x2]
        # 顔画像をリサイズする
        face_size = 256
        face_square = cv2.resize(
            face_area, (face_size, face_size), interpolation=cv2.INTER_AREA
        )

        write_pc_image(
            bot.guild_id,
            bot.user_id,
            state_data["pc_id"],
            cv2.imencode(".jpg", face_square)[1].tobytes(),
        )

    tz = datetime.timezone.utc
    now = datetime.datetime.now(tz)
    state_data["ts"] = now.timestamp()
    icon_url = get_pc_image_url(
        bot.guild_id, bot.user_id, state_data["pc_id"], now.timestamp()
    )

    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": "USER ICON",
                "description": "SET IMAGE",
                "color": 0x000000,
                "thumbnail": {"url": icon_url},
            }
        ],
    }
