import traceback

from aiogram import html
from aiogram.types import Message

from handlers.pidor import db
from handlers.pidor.utils import get_mention


async def pidorstats(message: Message) -> None:
    try:
        stats = await db.get_pidor_usage_stats(message.chat.id)
    except Exception:
        traceback.print_exc()
        stats = None

    if not stats:
        await message.reply("<b>Недостаточно данных. Попробуйте позже.</b>")
        return

    text = "<b>Статистика пидоров за последний год:</b>\n"
    for entry in stats:
        ends = [2, 3, 4]
        should_add_a = False
        for end in ends:
            if str(entry['number_of_occurrences']).endswith(str(end)):
                should_add_a = True

        text += ("\n" + html.bold(
            await get_mention(message, entry['user_id'], False)) +
                 " - " +
                 html.italic(entry['number_of_occurrences']) +
                 html.italic(" раза" if should_add_a else " раз")
                 )

    await message.answer(text)
