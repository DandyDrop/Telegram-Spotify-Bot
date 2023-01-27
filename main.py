import telebot
import requests
from bs4 import BeautifulSoup
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.patched import Message
from telethon.client import TelegramClient
from telethon.sessions import StringSession
bot = telebot.TeleBot("TOKEN")

def spotipars(playlist_url):
    links = []
    resp = requests.get(playlist_url)
    soup = str(BeautifulSoup(resp.text, "html.parser"))
    for i in range(30):
        soup = soup[soup.index('https://open.spotify.com/track'):]
        link = soup[:soup.index('"')]
        soup = soup[soup.index('"') + 1:]
        links.append(link)
    return links

async def send_and_press(message, check_times):
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
    done = False
    while check_times > 0 and not done:
        mes = await client.get_messages("@download_it_bot", limit=2)
#         print(f"Last mes:\n{mes[0].message}\n\n")
#         print(f"Prev mes:\n{mes[1].message}\n\n")
        for mes_one in mes:
            if "Saved by" in str(mes_one.message):
                mes_new = Message(id=mes_one.id, reply_markup=None, message=None, media=mes_one.media)
                await client.send_message(entity=to_chat, message=mes_new)
                done = True
                break

#         print("retrying")
        check_times -= 1
        time.sleep(10)

@bot.message_handler(commands=['spot'])
def main(m):
    # to be continued
    links_result = spotipars(link)
    for link_final in links_result:
        with TelegramClient(StringSession(os.environ.get("STRING_SESSION")), int(os.environ.get("API_ID")), os.environ.get("API_HASH")) as client:
            client.loop.run_until_complete(send_and_press(link_final, 50))
            client.loop.run_until_complete(send_result("BOT_USERNAME", 50))
        time.sleep(10)


bot.polling()
