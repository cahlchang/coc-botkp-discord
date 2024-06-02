import requests
import json
import os
import time
from dotenv import load_dotenv

def build_command_data(name: str,
                    description: str,
                    options_name: str,
                    options_description: str,
                    options_type: int,
                    options_required: bool)-> dict:
    return {
        "name": name,
        "description": description,
        "options": [
            {
                "name": options_name,
                "description": options_description,
                "type": options_type,
                "required": options_required,
            }
        ],
    }

def build_single_command_data(name: str, description: str)->dict:
    return {
        "name": name,
        "description": description
    }

if __name__ == "__main__":
    load_dotenv(".env")
    APP_ID = os.environ["APPLICATION_ID"]
    TOKEN = os.environ["TOKEN"]

    commands = []
    commands.append(build_command_data(name="cc",
                                    description="coc roll action",
                                    options_name="action",
                                    options_description="The name of the skill to execute",
                                    options_type=3,
                                    options_required=True))

    commands.append(build_command_data(name="init",
                                    description="init action",
                                    options_name="action",
                                    options_description="The URL of the character sheet for initializing the character",
                                    options_type=3,
                                    options_required=False))

    commands.append(build_command_data(name="sanc",
                                    description="SAN Check Action",
                                    options_name="value",
                                    options_description="The amount of SAN reduction for successful and failed SAN checks",
                                    options_type=3,
                                    options_required=False))

    commands.append(build_command_data(name="addimage",
                                    description="addimage",
                                    options_name="character-image",
                                    options_description="character image",
                                    options_type=11,
                                    options_required=True))

    commands.append(build_command_data(name="change-status",
                                    description="change status",
                                    options_name="value",
                                    options_description="change status(example hp-3)",
                                    options_type=3,
                                    options_required=True))

    commands.append(build_command_data(name="dice",
                                    description="DICE Roll",
                                    options_name="value",
                                    options_description="dice type and number(example 3d10)",
                                    options_type=3,
                                    options_required=False))
    commands.append(build_single_command_data(name="reload", description="reload the character sheet"))
    commands.append(build_single_command_data(name="status", description="show status"))


    ApiEndpoint = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    headers = {
        "content-type": "application/json",
        "Authorization": "Bot " + TOKEN,
    }

    for command in commands:
        response = requests.post(ApiEndpoint, data=json.dumps(command), headers=headers)
        print(response.status_code)
0-0        print(response.text)
        time.sleep(2)
