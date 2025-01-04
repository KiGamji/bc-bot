import traceback

from aiogram import html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message

from handlers.pidor import db


async def pidorstats(message: Message) -> None:
    try:
        stats = await db.get_pidor_usage_stats(message.chat.id)
    except Exception:
        traceback.print_exc()
        stats = None

    if not stats:
        await message.reply("<b>Недостаточно данных. Попробуйте позже.</b>")
        return

    async def get_username(user_id: int) -> str:
        try:
            member = await message.bot.get_chat_member(message.chat.id, user_id)
            if member.user.username is not None:
                name = f"{html.quote(member.user.username)}"
            else:
                name = html.quote(member.user.first_name)
        except (TelegramForbiddenError, TelegramBadRequest):
            name = user_id  # In worst case, use the user_id

        return name

    text = "<b>Статистика пидоров за последний год:</b>\n"
    for entry in stats:
        ends = [2, 3, 4]
        should_add_a = False
        for end in ends:
            if str(entry['number_of_occurrences']).endswith(str(end)):
                should_add_a = True

        text += ("\n" + html.bold(
            await get_username(entry['user_id'])) +
                 " - " +
                 html.italic(entry['number_of_occurrences']) +
                 html.italic(" раза" if should_add_a else " раз")
                 )

    await message.answer(text)
