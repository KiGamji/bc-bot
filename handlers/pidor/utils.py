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
    hours = seconds // 3600  # Get the whole hours
    if seconds % 3600 != 0:
        hours += 1  # If there's a remainder, add one hour to round up
    singular, few, many = 'час', 'часа', 'часов'
    name = get_russian_plural(hours, singular, few, many)
    return f'{hours} {name}'


async def get_mention(message: Message, target_id: int, should_notify: bool) -> str:
    try:
        member = await message.bot.get_chat_member(message.chat.id, target_id)
        user = member.user

        if user.username is not None:
            return f"@{html.quote(user.username)}" if should_notify else html.quote(user.username)
        else:
            return f'<a href="tg://user?id={target_id}">{html.quote(user.first_name)}</a>' if should_notify else html.quote(
                user.first_name)
    except (TelegramForbiddenError, TelegramBadRequest):
        return f'<a href="tg://user?id={target_id}">{target_id}</a>' if should_notify else html.quote(target_id)
