import json
import os
from yig.bot import Bot
from dotenv import load_dotenv

def run(event, lambda_context):
    print("start")
    load_dotenv(".env")
    if "body" not in event:
        return {
            'statusCode': 200,
            "body": json.dumps({"content": "not body"})
        }
    print("request-body exists")
    headers = { k.lower(): v for k, v in event['headers'].items() }
    req = json.loads(event['body'])
    APPLICATION_PUBLIC_KEY = os.environ.get("APPLICATION_PUBLIC_KEY")
    bot = Bot(APPLICATION_PUBLIC_KEY, req)
    if not bot.verify(headers.get('x-signature-ed25519'), headers.get('x-signature-timestamp'), event['body']):
        return {
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": 401,
            "headers": {},
            "body": "invalid request signature"
        }
    print("verified request")
    if req['type'] == 1:
        return {
            'statusCode': 200,
            "body": json.dumps({"type": 1})
        }
    else:
        bot.init_param()
        bot.dispatch()
    return None