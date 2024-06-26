from nacl.signing import VerifyKey
from importlib import import_module
from glob import glob
import urllib.parse
import os
import asyncio
import requests

command_manager: list = []


class Bot(object):
    def __init__(self, APPLICATION_PUBLIC_KEY, token ,req):
        self.verify_key = VerifyKey(bytes.fromhex(APPLICATION_PUBLIC_KEY))
        self.HEADERS = {"Content-Type": "application/json"}
        self._interaction = req
        self._bot_token = token
        self.init_plugins()

    def verify(self, signature: str, timestamp: str, event: str) -> bool:
        """
        Verify the signature of a Discord request.

        Parameters
        ----------
        signature : str
        The signature obtained from the X-Signature-Ed25519 HTTP request header.
        timestamp : str
        The timestamp obtained from the X-Signature-Timestamp HTTP request header.
        body : str
        Request payload

        Returns
        -------
        bool
        True if the signature is valid, False otherwise.

        Raises
        ------
        ValueError
        If the signature cannot be verified.

        Notes
        -----
        This method is used to verify the authenticity of a Discord request, using
        the request's signature, timestamp, and body. The signature is a HMAC-SHA256
        hash of the concatenation of the timestamp and body, generated using the
        client's secret key. If the signature is valid, the request is deemed to be
        authentic.

        Discord request headers contain the `X-Signature-Ed25519` and `X-Signature-Timestamp` fields, which correspond to `signature` and `timestamp` parameters, respectively.
        """
        try:
            self.verify_key.verify(
                f"{timestamp}{event}".encode(), bytes.fromhex(signature)
            )
        except Exception as e:
            print(f"failed to verify request: {e}")
            return False

        return True

    async def send_deferred_response(self, interaction_id, interaction_token):
        url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
        data = {
            "type": 5,  # 型5はDeferred Responseを示します。
            "data": {
                "content": "Processing your request. Please wait...",
            },
        }
        return requests.post(url, json=data, headers=self.HEADERS)

    def send_bot_content(self, application_id, interaction_token, content):
        try:
            print("content:", content)
            url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"
            res = requests.post(url, json=content, headers=self.HEADERS)
        except Exception as e:
            print(e.stack_trace(0))
            print(res)
            print(res.text)
            raise e
        return res

    def init_plugins(self):
        module_list = glob("yig/plugins/*.py")
        for module in module_list:
            module = module.split(".")[0]
            import_module(".".join(module.split("/")))

    def init_param(self):
        self._channel_id = urllib.parse.unquote(self._interaction["channel_id"])
        self._guild_id = urllib.parse.unquote(self._interaction["guild_id"])
        self._user_id = urllib.parse.unquote(self._interaction["member"]["user"]["id"])

        self._action_name = urllib.parse.unquote_plus(self._interaction["data"]["name"])
        self._action_data = self._interaction["data"]

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def guild_id(self):
        return self._guild_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def action_name(self):
        return self._action_name

    @property
    def action_data(self):
        return self._action_data

    @property
    def interaction(self):
        return self._interaction

    @property
    def bot_token(self):
        return self._bot_token

    async def process_and_respond_interaction(self, dispatch_function):
        interactive_id = self.interaction["id"]
        token = self.interaction["token"]
        task = asyncio.create_task(self.send_deferred_response(interactive_id, token))
        content = dispatch_function(self)
        await task
        return content

    def dispatch(self):
        for command_data in command_manager:
            if command_data["command"] == self.action_name:
                print("dispatch start")
                content = asyncio.run(
                    self.process_and_respond_interaction(command_data["function"])
                )
                token = self.interaction["token"]
                application_id = os.environ.get("APPLICATION_ID")
                response = self.send_bot_content(application_id, token, content)
                print(response)
                print(response.text)
        #         break
        # else:
        #     raise Exception("dispatch error")

        return False


def listener(command_string):
    def wrapper(self):
        global command_manager
        command_manager.append({"command": command_string, "function": self})

    return wrapper
