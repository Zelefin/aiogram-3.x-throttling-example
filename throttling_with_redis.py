from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, TelegramObject
from typing import Any
from collections.abc import Awaitable, Callable


class ThrottlingMiddlewareWithRedis(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self._storage = storage
        self.limit = 20

    async def __call__(
        self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: Message, data: dict[str, Any]
    ) -> Any:
        context = await self._storage.redis.get(str(event.from_user.id))
        if context:
            if int(context.decode()):
                await self._storage.redis.set(name=str(event.from_user.id), value=0, ex=self.limit)
                return await event.answer(f"Stop flood for 20 sec")
            return await event.answer(
                f"In flood till: {await self._storage.redis.ttl(name=str(event.from_user.id))} sec"
            )
        await self._storage.redis.set(name=str(event.from_user.id), value=1, ex=self.limit)
        return await handler(event, data)
