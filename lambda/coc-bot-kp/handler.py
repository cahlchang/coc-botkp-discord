import json
import os
from yig.bot import Bot
from dotenv import load_dotenv # type: ignore
import requests
import traceback

# import cProfile
# import pstats
# import io

# def run_with_profiling(event, lambda_context):
#     pr = cProfile.Profile()
#     pr.enable()
    
#     try:
#         run(event, lambda_context)
#     finally:
#         # pass
#         pr.disable()
#         s = io.StringIO()
#         ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
#         ps.print_stats()
#         print("Profiling results:")
#         print(s.getvalue())


def handle(event, lambda_context):
    try:
        run(event, lambda_context)
        # run_with_profiling(event, lambda_context)
    except Exception as e:
        webhook = os.environ.get("ERROR_WEBHOOK")
        stack_trace = traceback.format_exc()
        if webhook:
            requests.post(webhook, json={"content": f"An error occurred: {str(e)}\nStack trace:\n{stack_trace}"})
        else:
            print(f"ERROR_WEBHOOK is not set. Error: {str(e)}\nStack trace:\n{stack_trace}")

def run(event, lambda_context):
    print("start")
    if "body" not in event:
        return {"statusCode": 200, "body": json.dumps({"content": "not body"})}
    headers = {k.lower(): v for k, v in event["headers"].items()}
    req = json.loads(event["body"])
    load_dotenv(".env")

    APPLICATION_PUBLIC_KEY = os.environ.get("APPLICATION_PUBLIC_KEY")
    if not APPLICATION_PUBLIC_KEY:
        raise ValueError("Environment variable 'APPLICATION_PUBLIC_KEY' is not set")
    BOT_TOKEN = os.environ.get("TOKEN")
    if not BOT_TOKEN:
        raise ValueError("Environment variable 'TOKEN' is not set")

    APPLICATION_ID = os.environ.get("APPLICATION_ID")
    if not APPLICATION_ID:
        raise ValueError("Environment variable 'APPLICATION_ID' is not set")


    bot = Bot(APPLICATION_PUBLIC_KEY, APPLICATION_ID, BOT_TOKEN, req)
    if not bot.verify(
        headers.get("x-signature-ed25519"),
        headers.get("x-signature-timestamp"),
        event["body"],
    ):
        return {
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": 401,
            "headers": {},
            "body": "invalid request signature",
        }
    if req["type"] == 1:
        return {"statusCode": 200, "body": json.dumps({"type": 1})}
    else:
        bot.init_param()
        bot.dispatch()
    return None
