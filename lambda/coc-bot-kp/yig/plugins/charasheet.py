import requests
import re
from re import Match
import json
import unicodedata
import datetime
import traceback

from yig.bot import listener, Bot
from yig.util.data import (
    read_user_data,
    write_user_data,
    get_basic_status,
    get_user_param,
    get_now_status,
    create_error_response,
    create_heart_string,
    create_magic_point_string,
    create_san_string
)

from yig.util.view import (
    get_pc_image_url,
    create_param_image,
    save_param_image
)

import yig.config

@listener("init")
def init_charasheet(bot:Bot):
    matcher: Match[str] | None = re.match(r"(https.*)", bot.action_data["options"][0]["value"])
    if not matcher:
        raise ValueError("Invalid URL")
    url_plane: str = matcher.group(1)
    url: str = f"{url_plane}.json"
    response: requests.Response = requests.get(url)
    request_json: dict = json.loads(response.text)

    if request_json["game"] == "coc":
        user_param: dict = format_param_json_with_6(bot, request_json)
    elif request_json["game"] == "coc7":
        user_param: dict = format_param_json_with_7(bot, request_json)

    user_param["url"] = url_plane

    pc_id: str = user_param["pc_id"]
    key: str = f"{pc_id}.json"

    write_user_data(bot, bot.guild_id, bot.user_id, key, user_param)

    tz = datetime.timezone.utc
    now = datetime.datetime.now(tz)
    state_data = {
        "url": url,
        "pc_id": user_param["pc_id"],
        "ts": now.timestamp(),
    }

    write_user_data(
        bot, bot.guild_id, bot.user_id, yig.config.STATE_FILE_PATH, state_data
    )
    try:
        chara_response = build_chara_response(
            bot, "INIT", user_param, state_data, bot.guild_id, bot.user_id, pc_id
        )
    except Exception as e:
        return create_error_response("キャラクターシートの読み込みに失敗しました",
                                    ''.join(traceback.TracebackException.from_exception(e).format()))

    return chara_response


@listener("reload")
def update_charasheet_with_vampire(bot: Bot):
    state_data = read_user_data(bot, bot.guild_id, bot.user_id, yig.config.STATE_FILE_PATH)
    user_param_old = get_user_param(bot, bot.guild_id, bot.user_id, state_data["pc_id"])
    tz = datetime.timezone.utc
    now = datetime.datetime.now(tz)
    state_data["ts"] = now.timestamp()
    url = state_data["url"]
    res = requests.get(url)
    request_json = json.loads(res.text)
    if user_param_old["game"] == "coc":
        user_param = format_param_json_with_6(bot, request_json)
    elif user_param_old["game"] == "coc7":
        user_param = format_param_json_with_7(bot, request_json)

    user_param["url"] = user_param_old["url"]
    pc_id = user_param["pc_id"]
    key = f"{pc_id}.json"

    write_user_data(bot, bot.guild_id, bot.user_id, key, user_param)
    return build_chara_response(
        bot, "RELOAD", user_param, state_data, bot.guild_id, bot.user_id, pc_id
    )


def format_param_json_with_6(bot, request_json):
    param_json = {}

    REPLACE_PARAMETER = {
        "NP1": "STR",
        "NP2": "CON",
        "NP3": "POW",
        "NP4": "DEX",
        "NP5": "APP",
        "NP6": "SIZ",
        "NP7": "INT",
        "NP8": "EDU",
        "NP9": "HP",
        "NP10": "MP",
        "NP11": "初期SAN",
        "NP12": "アイデア",
        "NP13": "幸運",
        "NP14": "知識",
    }

    tba_replace = [
        "回避",
        "キック",
        "組み付き",
        "こぶし（パンチ）",
        "頭突き",
        "投擲",
        "マーシャルアーツ",
        "拳銃",
        "サブマシンガン",
        "ショットガン",
        "マシンガン",
        "ライフル",
    ]

    tfa_replace = [
        "応急手当",
        "鍵開け",
        "隠す",
        "隠れる",
        "聞き耳",
        "忍び歩き",
        "写真術",
        "精神分析",
        "追跡",
        "登攀",
        "図書館",
        "目星",
    ]

    taa_replace = [
        "運転",
        "機械修理",
        "重機械操作",
        "乗馬",
        "水泳",
        "製作",
        "操縦",
        "跳躍",
        "電気修理",
        "ナビゲート",
        "変装",
    ]

    tca_replace = ["言いくるめ", "信用", "説得", "値切り", "母国語"]

    tka_replace = [
        "医学",
        "オカルト",
        "化学",
        "クトゥルフ神話",
        "芸術",
        "経理",
        "考古学",
        "コンピューター",
        "心理学",
        "人類学",
        "生物学",
        "地質学",
        "電子工学",
        "天文学",
        "博物学",
        "物理学",
        "法律",
        "薬学",
        "歴史",
    ]

    for key, param in REPLACE_PARAMETER.items():
        param_json[param] = request_json[key]

    def replace_role_param(key, lst_key_roles):
        return_data = {}
        if f"{key}Name" in request_json:
            for custom_added_name in request_json[f"{key}Name"]:
                lst_key_roles.append(custom_added_name)

        for idx, param in enumerate(lst_key_roles):
            lst = []
            lst.append(request_json[f"{key}D"][idx])
            lst.append(request_json[f"{key}S"][idx])
            lst.append(request_json[f"{key}K"][idx])
            lst.append(request_json[f"{key}A"][idx])
            lst.append(request_json[f"{key}O"][idx])
            lst.append(request_json[f"{key}P"][idx])
            return_data[param] = [i if i != "" else 0 for i in lst]
        return return_data

    param_json.update(replace_role_param("TBA", tba_replace))
    param_json.update(replace_role_param("TFA", tfa_replace))
    param_json.update(replace_role_param("TAA", taa_replace))
    param_json.update(replace_role_param("TCA", tca_replace))
    param_json.update(replace_role_param("TKA", tka_replace))

    def add_spec_param(spec_param, name):
        param = request_json[spec_param]
        return {f"{name}（{param}）": param_json[name]}

    param_json.update(add_spec_param("unten_bunya", "運転"))
    param_json.update(add_spec_param("seisaku_bunya", "製作"))
    param_json.update(add_spec_param("main_souju_norimono", "操縦"))
    param_json.update(add_spec_param("mylang_name", "母国語"))
    param_json.update(add_spec_param("geijutu_bunya", "芸術"))

    param_json["現在SAN"] = request_json["SAN_Left"]
    param_json["開始SAN"] = request_json["SAN_Left"]
    param_json["最大SAN"] = request_json["SAN_Max"]

    param_json["user_id"] = bot.user_id
    param_json["name"] = request_json["pc_name"]
    param_json["pc_id"] = request_json["data_id"]
    param_json["DB"] = request_json["dmg_bonus"]
    param_json["memo"] = request_json["pc_making_memo"]
    param_json["job"] = request_json["shuzoku"]
    param_json["age"] = request_json["age"]
    param_json["sex"] = request_json["sex"]
    param_json["game"] = request_json["game"]
    param_json["arms_name"] = request_json["arms_name"]
    param_json["arms_hit"] = request_json["arms_hit"]
    param_json["arms_damage"] = request_json["arms_damage"]
    param_json["arms_attack_count"] = request_json["arms_attack_count"]
    param_json["item_name"] = request_json["item_name"]
    param_json["item_tanka"] = request_json["item_tanka"]
    param_json["item_num"] = request_json["item_num"]
    param_json["item_price"] = request_json["item_price"]
    param_json["item_memo"] = request_json["item_memo"]
    param_json["money"] = request_json["money"]
    param_json["game"] = request_json["game"]

    return param_json


def format_param_json_with_7(bot, request_json):
    param_json = {}

    REPLACE_PARAMETER = {
        "NP1": "STR",
        "NP2": "CON",
        "NP3": "DEX",
        "NP4": "APP",
        "NP5": "POW",
        "NP6": "SIZ",
        "NP7": "INT",
        "NP8": "EDU",
        "NP9": "MOV",
        "NP10": "HP",
        "NP11": "MP",
    }

    for key, param in REPLACE_PARAMETER.items():
        param_json[param] = request_json[key]

    for idx, skill_name in enumerate(request_json["SKAN"]):
        fuki_name = request_json["SKAM"][idx]

        if fuki_name == "*":
            skill_name = f"{skill_name}【any】"
        elif fuki_name != "":
            skill_name = f"{skill_name}【{fuki_name}】"

        lst = [
            request_json["SKAD"][idx],
            request_json["SKAS"][idx],
            request_json["SKAK"][idx],
            request_json["SKAA"][idx],
            request_json["SKAO"][idx],
            request_json["SKAP"][idx],
        ]
        lst = [i if i != "" else "0" for i in lst]
        param_json[skill_name] = lst

    param_json["現在SAN"] = request_json["SAN_Left"]
    param_json["開始SAN"] = request_json["SAN_start"]
    param_json["最大SAN"] = request_json["SAN_Max"]

    param_json["幸運"] = request_json["Luck_Left"]
    param_json["幸運開始時"] = request_json["Luck_start"]

    param_json["user_id"] = bot.user_id
    param_json["name"] = request_json["pc_name"]
    param_json["pc_id"] = request_json["data_id"]
    param_json["DB"] = request_json["dmg_bonus"]
    param_json["job"] = request_json["shuzoku"]
    param_json["age"] = request_json["age"]
    param_json["sex"] = request_json["sex"]
    param_json["game"] = request_json["game"]
    param_json["arms_name"] = request_json["arms_name"]
    param_json["arms_hit"] = request_json["arms_hit"]
    param_json["arms_damage"] = request_json["arms_damage"]
    param_json["arms_attack_count"] = request_json["arms_attack_count"]
    param_json["item_name"] = request_json["item_name"]
    param_json["item_tanka"] = request_json["item_tanka"]
    param_json["item_num"] = request_json["item_num"]
    param_json["item_price"] = request_json["item_price"]
    param_json["item_memo"] = request_json["item_memo"]
    param_json["money"] = request_json["money"]

    return param_json


def build_chara_response(bot, title, user_param, state_data, guild_id, user_id, pc_id):
    now_hp, max_hp, now_mp, max_mp, now_san, max_san, db = get_basic_status(
        user_param, state_data
    )

    if user_param["game"] == "coc7":
        now_luck = get_now_status("幸運", user_param, state_data)
        luck_left = user_param["幸運"]
        luck_start = user_param["幸運開始時"]

    pc_name = user_param["name"]
    dex = user_param["DEX"]
    chara_url = user_param["url"]
    job = user_param["job"]
    age = user_param["age"]
    sex = user_param["sex"]
    skill_data = {}
    for key, param in user_param.items():
        if isinstance(param, list) and len(param) == 6:  # 保管庫のjson都合
            if sum([int(s) for s in param][1:4]) == 0:
                continue
            if key in ("製作", "芸術", "母国語") and user_param["game"] == "coc":
                continue
            skill_point = int(param[5])
            if skill_point != 0:
                skill_data[key] = skill_point
    sorted_skill_data = sorted(skill_data.items(), key=lambda x: x[1], reverse=True)
    skill_message = ""

    def get_east_asian_width_count(text):
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in "FWA":
                count += 2
            else:
                count += 1
        return count

    cnt_word = 0
    for skill_data in sorted_skill_data:
        skill_name, skill_point = skill_data
        cnt_word += get_east_asian_width_count(f"**{skill_name}:** {skill_point}% ")
        if 100 < cnt_word:
            skill_message += "\n"
            cnt_word = 0

        skill_message += f"**{skill_name}:** {skill_point}% "

    image = create_param_image(bot, user_param)
    param_image_url = save_param_image(
        bot,
        image,
        guild_id,
        user_id,
        user_param["pc_id"])
    param_image_url += "?%s" % state_data["ts"]
    param_message = ""
    for name in ["STR", "CON", "POW", "DEX", "APP", "SIZ", "INT", "EDU"]:
        if name == "EDU":
            param_message += "**%s:**%s" % (name, user_param[name])
        elif name == "DEX":
            param_message += "**%s:**%s \n" % (name, user_param[name])
        else:
            param_message += "**%s:**%s | " % (name, user_param[name])

    line3 = ""
    hp_string = create_heart_string(int(now_hp), int(max_hp))
    mp_string = create_magic_point_string(int(now_mp), int(max_mp))
    san_string = create_san_string(int(now_san))
    if user_param["game"] == "coc":
        line3 = f"\n**HP: ** {now_hp}/{max_hp} {hp_string} \n**MP:** {now_mp}/{max_mp} {mp_string} \n**SAN:** {now_san}/{max_san} {san_string}"
    elif user_param["game"] == "coc7":
        line3 = f"\n**HP: ** {now_hp}/{max_hp} **MP:** {now_mp}/{max_mp} **SAN: {now_san}/{max_san} **DEX: ** {dex} **DB:** {db} **Luck:** {now_luck}/{luck_start}/99\n"

    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "description": "",
                "title": f"**{title}**",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": f"**{pc_name}**",
                        "value": (
                            line3
                        )
                    }
                ],
                "inline": False,
                "thumbnail": {
                    "url": get_pc_image_url(guild_id, user_id, pc_id, state_data["ts"])
                }
            },
            {
                "type": "rich",
                "description": "",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "",
                        "value": f"**JOB: ** {job}  \n**AGE: ** {age} **DB: ** {db} **GENDER: ** {sex}\n"
                        + param_message
                    }
                ],
                "inline": False,
                "thumbnail": {
                    "url": param_image_url
                }
            },
            {
                "type": "rich",
                "description": skill_message,
                "color": 0x2ecc71,
                "inline": False
            }
        ]
    }
