from aiogram import html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from main import bot


async def get_mention(chat_id: int, user_id: int, notify: bool) -> str:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        user = member.user

        username = user.username
        first_name = user.first_name

        if username:
            return (
                f"@{html.quote(username)}"
                if notify
                else html.quote(username)
            )
        else:
            return (
                f'<a href="tg://user?id={user_id}">{html.quote(first_name)}</a>'
                if notify
                else html.quote(first_name)
            )

    except (TelegramBadRequest, TelegramForbiddenError):
        return (
            f'<a href="tg://user?id={user_id}">{user_id}</a>'
            if notify
            else html.quote(str(user_id))
        )
