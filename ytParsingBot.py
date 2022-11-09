import hashlib
import os

from youtube_search import YoutubeSearch
from config import TOKEN, URL_APP
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import psycopg2 as ps


def searcher(text):
    res = YoutubeSearch(text, max_results=10).to_dict()
    return res


base = ps.connect(os.environ.get('DATABASE_URL'), sslmode='require')
cur = base.cursor()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def on_startup(dp):
    await bot.set_webhook(URL_APP)


async def on_shutdown(dp):
    await bot.delete_webhook()
    cur.close()
    base.close()


@dp.message_handler()
async def start(message: types.Message):
    await message.answer('Не надо мне писать, это инлайн бот!')


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    text = query.query or 'echo'
    links = searcher(text)

    articles = [types.InlineQueryResultArticle(
        id=hashlib.md5(f'{link["id"]}'.encode()).hexdigest(),
        title=f'{link["title"]}',
        url=f'https://www.youtube.com/watch?v={link["id"]}',
        thumb_url=f'{link["thumbnails"][0]}',
        input_message_content=types.InputTextMessageContent(
            message_text=f'https://www.youtube.com/watch?v={link["id"]}'))
        for link in links]
    await query.answer(articles, cache_time=60, is_personal=True)

@dp.chosen_inline_handler()
async def chosen(chosen_res: types.ChosenInlineResult):
    text = chosen_res.query

    cur.execute("SELECT search from searcher WHERE search = %s", (text,))
    res = cur.fetchone()
    print('заебало')
    print(res)

    if not res:
        cur.execute("INSERT INTO searcher(search, count) VALUES (%s, %s)", (text, 1))
        base.commit()
    else:
        cur.execute("UPDATE searcher SET count = count + 1 WHERE search = %s", (text,))
        base.commit()



executor.start_webhook(
    dispatcher=dp,
    webhook_path='',
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    skip_updates=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)))
