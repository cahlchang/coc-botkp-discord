from yig.bot import listener, Bot

from yig.util.data import create_new_channel, create_invite_link, send_message_to_channel, get_bot_role_id
from datetime import datetime

@listener("start-session")
def start_session_command(bot: Bot):
    name = bot.action_data["options"][0]["value"]
    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y%m%d')
    name = f'{formatted_date}-{name}'

    bot_role_id = get_bot_role_id(bot.bot_token, bot.guild_id)
    if not bot_role_id:
        print("Failed to get bot role ID. Cannot create channel.")
        return None
    print("bot_role_id: ", bot_role_id)
    # チャンネルを作成
    new_channel = create_new_channel(
        bot_token=bot.bot_token, guild_id=bot.guild_id, user_id=bot.user_id, bot_role_id=bot_role_id, name=name
    )

    if new_channel:
        channel_id = new_channel['id']

        # 招待リンクを作成
        invite_link = create_invite_link(bot.bot_token, channel_id)

        if invite_link:
            # チャンネルに招待リンクを送信
            message_content = f'このチャンネルの招待リンク: {invite_link}'
            if send_message_to_channel(bot.bot_token, channel_id, message_content):
                message = 'チャンネルが作成され、招待リンクが送信されました'
            else:
                message = 'チャンネルと招待リンクは作成されましたが、メッセージの送信に失敗しました'
                # 上手くいかないので、一時的に元のメッセージに渡す
                #message = f'新しくチャンネルが作成されました。\n{name}\n 招待リンク: {invite_link}'
                # 権限系は見直し必要
                message = f'新しくチャンネルが作成されました。\n{name}'#\n 招待リンク: {invite_link}'
        else:
            message = 'チャンネルは作成されましたが、招待リンクの作成に失敗しました'
    else:
        message = 'チャンネルの作成に失敗しました'

    print(f"最終結果: {message}")

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
