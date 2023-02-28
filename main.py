import asyncio
import time
import traceback
import aiohttp
from product import Product


######################################################## CONFIG ########################################################


PRODUCTS = [
    Product("RPi", "https://botland.com.pl/raspberry-pi-3a/13834-zestaw-raspberry-pi-3a-wifi-oryginalna-obudowa-zasilacz-5v25a-5903351241526.html"),
    Product("RPi Obudowa", "https://kamami.pl/raspberry-pi-3-model-a/573175-raspberry-pi-3-model-a-z-wifi-24-i-5-ghz-oraz-bluetooth-42.html")
]

TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
CHAT_ID = 12345678
DELAY = 10


########################################################################################################################


async def send_message(text):
    session = aiohttp.ClientSession()
    await session.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "markdown"
        }
    )
    await session.close()


async def poll():
    while True:
        await asyncio.sleep(DELAY)
        for product in PRODUCTS:
            try:
                await product.check_updates()
                if product.notify():
                    a = "jest już dostępny!!!" if product.available else "nie jest już dostępny."
                    await send_message(f"[{product.name}]({product.url}) {a}")
            except:
                print(traceback.format_exc())


def bot_start():
    return "*Witaj!*\n" \
           "Jestem botem który sprawdza dostępność produktów na podanych sklepach i powiadamia o ich dostępności.\n\n" \
           "Wpisz /status by sprawdzić czy działam poprawnie."


def bot_status():
    summary = "✅ Wszystko działa poprawnie"
    full_list = "" if len(PRODUCTS) else "_Brak produktów_"
    now = time.time()
    for product in PRODUCTS:
        ago = round(now - product.updated)
        if ago <= DELAY + len(PRODUCTS):
            mark = "✅" if product.available else "❌"
        else:
            mark = "⚠️"
            summary = "⚠️ Wykryto problemy"
        full_list += f"{mark} `[{ago}s] `[{product.name}]({product.url}) na {product.get_origin()}\n"
    return f"`---------------- Status ----------------`\n\n_{summary}_\n\n{full_list}"


async def bot():
    offset = 0
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    print("Bot started")
    while True:
        await asyncio.sleep(2)
        async with aiohttp.ClientSession() as session:
            response = await session.get(f"{api}?offset={offset}")

            if response.status == 200:
                updates = (await response.json())["result"]
                for update in updates:
                    if update["update_id"] >= offset:
                        offset = update["update_id"] + 1

                    message = update["message"]
                    if message["from"]["id"] != CHAT_ID:
                        continue

                    if message["text"] == "/start":
                        await send_message(bot_start())

                    elif message["text"] == "/status":
                        await send_message(bot_status())


tasks = [bot(), poll()]


async def main():
    await asyncio.gather(*tasks)


asyncio.run(main())

