from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Any
from collections.abc import Awaitable, Callable
import time


class ThrottlingMiddlewareWithoutRedis(BaseMiddleware):
    def __init__(self):
        self.limit = 20

    async def __call__(
        self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: Message, data: dict[str, Any]
    ) -> Any:

        state: FSMContext = data['state']
        context = await state.get_data()

        if context and (time.time() - context["last_request"] < self.limit):
            # if context["Defined"]:
            #     return  # just ignore every update from this user
            # else:
            # await state.update_data(Defined=True)
            return await event.answer(
                f"Stop flood for {round(self.limit - (time.time() - context['last_request']), 2)} sec"
            )

        await state.update_data(last_request=time.time())  # Defined=False

        return await handler(event, data)
