import aiohttp
import time
from bs4 import BeautifulSoup


def available_kamami(html):
    result = html.find("span", {"id": "product-availability"}).text.lower()
    return "obecnie brak" not in result


def available_botland(html):
    result = html.find("div", {"id": "product-availability"}).text.lower()
    return "dostępny" in result and "oczekiwania" not in result


class Product:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.ok = False
        self.available = False
        self.available_last = False
        self.updated = 0
        self.updated_last = 0

    async def check_updates(self):
        session = aiohttp.ClientSession()
        resp = await session.get(self.url)

        if resp.status != 200:
            self.ok = False
            await session.close()
            return False

        self.ok = True
        self.updated_last = self.updated
        self.updated = time.time()
        raw = await resp.text()
        html = BeautifulSoup(raw, "html.parser")

        self.available_last = self.available
        if "https://kamami.pl/" in self.url:
            self.available = available_kamami(html)
        elif "https://botland.com.pl/" in self.url:
            self.available = available_botland(html)

        await session.close()
        return True

    def notify(self):
        became_available = self.available and not self.available_last
        became_unavailable = not self.available and self.available_last
        return (became_available or became_unavailable) and self.updated_last

    def is_available(self):
        return self.available

    def get_origin(self):
        a1 = self.url.find("://") + 3
        origin = self.url[a1:]
        a2 = origin.find("/")
        origin = origin[:a2]
        origin = origin[:origin.find(".")]
        return origin.title()

