from asyncio import sleep
from datetime import datetime, timedelta
from random import choice

from aiogram import html
from aiogram.filters import CommandObject
from aiogram.types import Message, ReactionTypeEmoji

from .db import PidorDatabase
from .strings import BEGINNING_STRINGS, PROCESS_STRINGS, FINAL_STRINGS
from .utils import format_timedelta_ru
from handlers.utils import get_mention

db = PidorDatabase()

locks = {}


async def pidor_command(message: Message, command: CommandObject) -> None:
    args = command.args
    if not args:
        await get_pidor(message)
        return

    is_pidor = await db.is_pidor(message.chat.id, message.from_user.id)

    if args == "register":
        if not is_pidor:
            await db.register(message.chat.id, message.from_user.id)
            await message.react([ReactionTypeEmoji(emoji="👌")])
        else:
            await message.reply(
                html.bold("ℹ️ Вы уже зарегистрированы в игре!"))

    elif args == "unregister":
        if is_pidor:
            await db.unregister(message.chat.id, message.from_user.id)
            await message.react([ReactionTypeEmoji(emoji="👌")])
        else:
            await message.react([ReactionTypeEmoji(emoji="🤔")])

    elif args == "stats":
        await get_stats(message)

    else:
        await message.react([ReactionTypeEmoji(emoji="🤔")])


async def get_pidor(message: Message) -> None:
    chat_id = message.chat.id

    # Ensure a single run per chat to prevent race conditions.
    if chat_id in locks.keys():
        return
    else:
        locks[chat_id] = True

    try:
        check_result = await db.get_last_usage(chat_id)
        if check_result:
            pidor_id, last_used = check_result
            next_use = last_used + 86400
            current_timestamp = int(datetime.now().timestamp())
            cooldown = next_use - current_timestamp

            # Cooldown has not expired yet
            if cooldown > 0:
                delta = timedelta(seconds=cooldown)
                time_left = format_timedelta_ru(delta)

                mention = await get_mention(chat_id, pidor_id, False)

                await message.reply(
                    f'<b>😋 Сегодняшний "победитель"</b> - {mention}\n'
                    f"🍌 Нового <b>пидора</b> можно будет выбрать через <b>{time_left}</b>."
                )
                return

        pidors = await db.get_from_chat(chat_id)
        if not pidors:
            await message.reply(
                "<b>🤔 Никто не зарегистрирован в игре. Зарегистрироваться -</b> "
                "<code>/pidor register</code>"
            )
            return

        pidor_id = choice(pidors)
        mention = await get_mention(chat_id, pidor_id, True)

        await message.answer(choice(BEGINNING_STRINGS))
        await sleep(3)

        await message.answer(choice(PROCESS_STRINGS))
        await sleep(3)

        await message.answer(choice(PROCESS_STRINGS))
        await sleep(3)

        await message.answer(choice(FINAL_STRINGS) + mention)
        await db.log_usage(chat_id, pidor_id)

    finally:
        del locks[chat_id]


async def get_stats(message: Message) -> None:
    chat_id = message.chat.id
    stats = await db.get_stats(chat_id)

    if not stats:
        await message.reply(
            html.italic("Ой, здесь ничего нет!") + "\n"
            "Нет данных за выбранный период."
        )
        return

    text = html.bold(f"📊 Пидоры за {datetime.now().year} год:") + "\n"
    for entry in stats:
        user_id = entry['user_id']
        times = entry['times']

        times_word = "раз"
        ends = [2, 3, 4]
        for end in ends:
            if str(times).endswith(str(end)):
                times_word = "раза"
                break

        user = await get_mention(chat_id, user_id, False)

        text += "\n" + html.bold(user) + " - " + html.italic(f"{times} {times_word}")

    await message.answer(text)
