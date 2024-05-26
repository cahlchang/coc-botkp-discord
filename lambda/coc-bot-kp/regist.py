import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")

APP_ID = os.environ["APPLICATION_ID"]
TOKEN = os.environ["TOKEN"]


def main():
    CommandData = {
        "name": "cc",
        "description": "coc roll action",
        "options": [
            {
                "name": "action",
                "description": "The name of the skill to execute",
                "type": 3,
                "required": True,
            }
        ],
    }
    c = {
        "name": "init",
        "description": "init action",
        "options": [
            {
                "name": "action",
                "description": "The URL of the character sheet for initializing the character",
                "type": 3,
            }
        ],
    }
    c_sanc = {
        "name": "sanc",
        "description": "SAN Check Action",
        "options": [
            {
                "name": "value",
                "description": "The amount of SAN reduction for successful and failed SAN checks",
                "type": 3,
            }
        ],
    }

    c_add_image = {
        "name": "addimage",
        "description": "addimage",
        "options": [
            {
                "type": 11,
                "name": "character-image",
                "description": "characterimage",
                "required": True,
            }
        ],
    }

    c_change_status = {
        "name": "change-status",
        "description": "change status",
        "options": [
            {
                "name": "value",
                "description": "change status",
                "type": 3,
            }
        ],
    }

    c_dice = {
        "name": "dice",
        "description": "DICE Roll",
        "options": [
            {
                "name": "value",
                "description": "roll the dice",
                "type": 3,
            }
        ],
    }

    single_command = [
        ["reload", "reload the character sheet"],
        ["status", "show status"],
    ]

    ApiEndpoint = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {
        "content-type": "application/json",
        "Authorization": "Bot " + TOKEN,
    }

    # for c in single_command:
    #     body = {"name": c[0], "description": c[1]}
    #     response = requests.post(ApiEndpoint, data=json.dumps(body), headers=headers)
    #     print(response.status_code)
    #     print(response.text)

    response = requests.post(ApiEndpoint, data=json.dumps(c_change_status), headers=headers)
    print(response.status_code)
    print(response.text)


main()
