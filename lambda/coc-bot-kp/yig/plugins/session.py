from yig.bot import listener, Bot

from yig.util.data import create_new_channel
from datetime import datetime

@listener("start-session")
def start_session_command(bot :Bot):
    name = bot.action_data["options"][0]["value"]

    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y%m%d')
    name = f'{formatted_date}-{name}'
    message = create_new_channel(
        bot_token=bot.bot_token, guild_id=bot.guild_id, user_id=bot.user_id, name=name
    )

    return {
        "content": "",
        "embeds": [
            {
                "type": "rich",
                "title": message,
                "description": "start-session",
                "color": 0x000000
            }
        ],
    }
