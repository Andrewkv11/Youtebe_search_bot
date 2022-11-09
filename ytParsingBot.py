import hashlib
import os

from youtube_search import YoutubeSearch
from config import TOKEN, URL_APP
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


def searcher(text):
    res = YoutubeSearch(text, max_results=10).to_dict()
    return res


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def on_startup(dp):
    await bot.set_webhook(URL_APP)


async def on_shutdown(dp):
    await bot.delete_webhook()


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


executor.start_webhook(
    dispatcher=dp,
    webhook_path='',
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    skip_updates=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)))
