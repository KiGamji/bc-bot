from aiogram import html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from main import bot


def get_russian_plural(n, singular, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return singular
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return few
    else:
        return many


def format_timedelta_ru(delta):
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    if seconds % 3600 != 0:
        hours += 1  # If there's a remainder, add one hour to round up
    singular, few, many = 'час', 'часа', 'часов'
    plural = get_russian_plural(hours, singular, few, many)
    return f'{hours} {plural}'


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
