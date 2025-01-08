from aiogram import html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message


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


async def get_mention(message: Message, target_id: int, notify: bool) -> str:
    try:
        member = await message.bot.get_chat_member(message.chat.id, target_id)
        user = member.user

        username = user.username
        first_name = user.first_name

        if username:
            return f"@{html.quote(username)}"
        else:
            return f'<a href="tg://user?id={target_id}">{html.quote(user.first_name)}</a>'

        if notify:
            return mention
        else:
            return html.quote(username if username else first_name)

    except (TelegramForbiddenError, TelegramBadRequest):
        return (
            f'<a href="tg://user?id={target_id}">{target_id}</a>'
            if notify
            else html.quote(str(target_id))
        )
