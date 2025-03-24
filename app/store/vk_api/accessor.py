import typing
from urllib.parse import urlencode, urljoin
from aiohttp.client import ClientSession
from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        method = "groups.getLongPollServer"
        params = {
            "group_id": self.app.config.bot.group_id,
            "access_token": self.app.config.bot.token
        }
        url = self._build_query("https://api.vk.com/method/", method, params)

        async with self.session.get(url) as response:
            data = await response.json()
            self.server = data["response"]["server"]
            self.key = data["response"]["key"]
            self.ts = data["response"]["ts"]

    async def poll(self):
        url = f"{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait=25"
        async with self.session.get(url) as response:
            data = await response.json()
            self.ts = data["ts"]
            return [
                Update(type=u["type"], object=UpdateObject(
                    message=UpdateMessage(
                        from_id=u["object"]["message"]["from_id"],
                        text=u["object"]["message"]["text"],
                        id=u["object"]["message"]["id"]
                    )
                )) for u in data.get("updates", [])
            ]

    async def send_message(self, message: Message) -> None:
        method = "messages.send"
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "random_id": 0,
            "access_token": self.app.config.bot.token
        }
        url = self._build_query("https://api.vk.com/method/", method, params)
        async with self.session.post(url) as response:
            await response.json()