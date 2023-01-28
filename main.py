import os
import time
import random
import telebot
import requests
import asyncio
from bs4 import BeautifulSoup
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.patched import Message
from telethon.client import TelegramClient
from telethon.sessions import StringSession
import flask
from flask import Flask, request, Response

bot = telebot.TeleBot(os.environ.get("TOKEN"))
app = Flask(__name__)
client = TelegramClient(StringSession(os.environ.get("STRING_SESSION")), int(os.environ.get("API_ID")),
                                    os.environ.get("API_HASH"))

def mistake(message):
    bot.send_message(chat_id=message.from_user.id,
                     text="Wrong request, here are some right request examples:\n"
                          "/spot https://open.spotify.com/playlist/37i9dQZF1DWWY64wDtewQt"
                          "")


@app.route('/', methods=['POST', 'GET'])
def handle_request():
    if request.headers.get('content-type') == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return ""
    else:
        flask.abort(403)
    if request.method == "POST":
        return Response("OK", status=200)
    else:
        return ""


@bot.message_handler(commands=['start'])
def on_start(m):
    bot.send_message(chat_id=m.chat.id,
                     text="Hello, I can download whole spotify playlist for you.\n"
                          "Just send me a message in this format:\n"
                          "/spot https://open.spotify.com/playlist/37i9dQZF1DWWY64wDtewQt"
                          "")


def spotipars(playlist_url):
    bot.send_message("@spotilo", "Accessed spotipars")
    links = []
    resp = requests.get(playlist_url)
    soup = str(BeautifulSoup(resp.text, "html.parser"))
    for i in range(30):
        soup = soup[soup.index('https://open.spotify.com/track'):]
        link = soup[:soup.index('"')]
        if link not in links:
            soup = soup[soup.index('"') + 1:]
            links.append(link)
        else: 
            break
    return links


async def send_and_press(message, check_times):
    bot.send_message("@spotilo", f"Accessed send_and_press with message:\n{message}")
    await client.send_message("@download_it_bot", message)
    for i in range(check_times):
        mes = await client.get_messages("@download_it_bot", limit=1)
        if str(mes[0].reply_markup) != "None":
            await client(GetBotCallbackAnswerRequest(
                peer=mes[0].peer_id,
                msg_id=mes[0].id,
                data=mes[0].reply_markup.rows[0].buttons[0].data
            ))
            break
        elif i == check_times - 1:
            await client.send_message(entity="@AUniqD",
                                      message="mistake, seems like download bot doesnt respond to mes at first")
        else:
            time.sleep(2)


async def send_result(to_chat, check_times):
    bot.send_message("@spotilo", f"Accessed send_result with to_chat =\n{to_chat}")
    done = False
    while check_times > 0 and not done:
        mes = await client.get_messages("@download_it_bot", limit=2)
        for mes_one in mes:
            if "Saved by" in str(mes_one.message):
                mes_new = Message(id=mes_one.id, reply_markup=None, message=None, media=mes_one.media)
                await client.send_message(entity=to_chat, message=mes_new)
                done = True
                break

        check_times -= 1
        time.sleep(10)

    if not done:
        await client.send_message(entity="@AUniqD",
                                  message="mistake, seems like download bot doesnt respond to mes at second")


async def spotify_main(playlist_url):
    bot.send_message("@spotilo", f"Accessed spotify_main with\n{playlist_url}")
    links_result = spotipars(playlist_url)
    for link_final in links_result:
        async with client:
            await send_and_press(link_final, 50)
            await send_result(os.environ.get("BOT_USERNAME"), 50)
        await asyncio.sleep(random.randint(7, 12))

@bot.message_handler(commands=['spot'])
def spotify_trigger(m):
    if m.text != "/spot":
        try:
            bot.send_message(m.chat.id, "Processing...")
            playlist_url = m.text[6:]
            asyncio.run(spotify_main(playlist_url))
        except Exception as e:
            e = str(e)
            bot.send_message(chat_id=m.chat.id, text=f"Got an error, try again, please. Error text:\n{e}")
    else:
        mistake(m)


def main():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))


if __name__ == '__main__':
    main()


