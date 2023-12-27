import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage

from throttling_with_redis import ThrottlingMiddlewareWithRedis
# from throttling_wo_redis import ThrottlingMiddlewareWithoutRedis

TOKEN = "..."

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.full_name}!")


@router.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.MARKDOWN)
    storage = RedisStorage.from_url("redis://localhost:6379/0")
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    dp.message.middleware(ThrottlingMiddlewareWithRedis(storage=storage))
    # dp.message.middleware(ThrottlingMiddlewareWithoutRedis()) # By default storage is MemoryStorage
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
