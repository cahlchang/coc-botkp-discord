from nacl.signing import VerifyKey
from importlib import import_module
from glob import glob
import urllib.parse
import os
import asyncio
import requests


import importlib
from typing import Union, Callable


class LazyImport:
    def __init__(self, module_or_func: Union[str, Callable, dict[str, str]]):
        self.module_or_func = module_or_func
        self._module = None

    def __call__(self) -> any:
        if self._module is None:
            if isinstance(self.module_or_func, str):
                self._module = importlib.import_module(self.module_or_func)
            elif isinstance(self.module_or_func, dict):
                self._module = type('LazyModule', (), {
                    k: LazyImport(v) for k, v in self.module_or_func.items()
                })()
            else:
                self._module = self.module_or_func()
        return self._module

    def __getattr__(self, name: str) -> any:
        if self._module is None:
            self._module = self()
        return getattr(self._module, name)


command_manager: list = []
class Bot(object):

    def __init__(self, APPLICATION_PUBLIC_KEY, APPLICATION_ID, token ,req):
        self.verify_key = VerifyKey(bytes.fromhex(APPLICATION_PUBLIC_KEY))
        self.HEADERS = {"Content-Type": "application/json"}
        self._interaction = req
        self._bot_token = token
        self._application_id = APPLICATION_ID
        self.init_plugins()

    def lazy_library_imports(self):
        self._lazy_imports = {
            'boto3': LazyImport('boto3'),
            'numpy': LazyImport('numpy'),
            'PIL': LazyImport({
                'Image': 'PIL.Image',
                'ImageDraw': 'PIL.ImageDraw',
                'ImageFont': 'PIL.ImageFont'
            }),
            'ClientError': LazyImport(lambda: importlib.import_module('botocore.exceptions').ClientError),
        }

    def __getattr__(self, name: str) -> any:
        if name not in self._lazy_imports:
            if name == 'boto3':
                self._lazy_imports[name] = LazyImport('boto3')
            elif name == 'numpy':
                self._lazy_imports[name] = LazyImport('numpy')
            elif name == 'PIL':
                self._lazy_imports[name] = LazyImport({
                    'Image': 'PIL.Image',
                    'ImageDraw': 'PIL.ImageDraw',
                    'ImageFont': 'PIL.ImageFont'
                })
            elif name == 'ClientError':
                self._lazy_imports[name] = LazyImport(lambda: importlib.import_module('botocore.exceptions').ClientError)
            else:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self._lazy_imports[name]()

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
    def application_id(self):
        return self._application_id

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
        self.lazy_library_imports()
        content = dispatch_function(self)
        await task
        return content

    def dispatch(self):
        for command_data in command_manager:
            if command_data["command"] == self.action_name:
                print("dispatch start. :", self.action_name)
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
