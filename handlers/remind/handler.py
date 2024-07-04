import re
from datetime import datetime, timedelta

import aiosqlite
from aiogram import html
from aiogram.filters import CommandObject
from aiogram.methods import SetMessageReaction
from aiogram.types import Message, ReactionTypeEmoji

from main import bot
from .scheduler_manager import main_sched


async def remind_command(message: Message, command: CommandObject) -> None:
    args = command.args
    if args:
        args = args.split(' ', 1)
        if len(args) < 2:
            await message.reply(
                "<b>🚫 Использование:</b> /remind [<i>время</i>] [<i>текст</i>]")
            return

        delay, reminder_text = args
        delay_pattern = re.compile(r"(\d+)([MwdhmsМндчмс])")
        match = delay_pattern.match(delay)
        if not match:
            await message.reply(
                "<b>🚫 Неверный формат времени.\n"
                + "Используйте следующие обозначения:</b>\n"
                + "– <b>M</b> — для месяцев\n"
                + "– <b>w</b> или <b>н</b> — для недель\n"
                + "– <b>d</b> или <b>д</b> — для дней\n"
                + "– <b>h</b> или <b>ч</b> — для часов\n"
                + "– <b>m</b> или <b>м</b> — для минут\n"
                + "– <b>s</b> или <b>с</b> — для секунд"
            )
            return

        amount, unit = match.groups()
        amount = int(amount)
        delta = {
            # English
            "M": timedelta(days=amount * 30),
            "w": timedelta(weeks=amount),
            "d": timedelta(days=amount),
            "h": timedelta(hours=amount),
            "m": timedelta(minutes=amount),
            "s": timedelta(seconds=amount),

            # Cyrillic
            "М": timedelta(days=amount * 30),
            "н": timedelta(weeks=amount),
            "д": timedelta(days=amount),
            "ч": timedelta(hours=amount),
            "м": timedelta(minutes=amount),
            "с": timedelta(seconds=amount),
        }[unit]

        remind_time = datetime.now() + delta

        # Limit maximum reminder time to 1 year
        limit = datetime.now() + timedelta(days=365)
        if remind_time < limit:
            async with aiosqlite.connect('./data/reminders.db') as db:
                await db.execute("INSERT INTO reminders (chat_id, user_id, username, text, remind_time) VALUES (?, ?, ?, ?, ?)",
                                 (message.chat.id, message.from_user.id, message.from_user.username, reminder_text, remind_time))
                await db.commit()

            main_sched.add_job(
                send_reminder,
                'date',
                run_date=remind_time,
                args=[
                    message.chat.id,
                    message.from_user.id,
                    message.from_user.username,
                    reminder_text,
                ],
            )

            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[
                    ReactionTypeEmoji(emoji="✍")
                ],
            )
        else:
            await message.reply(
                html.bold("🚫 Вы не можете установить напоминание дольше, чем на 1 год."))
    else:
        await message.reply(
            "<b>🚫 Использование:</b> /remind [<i>время</i>] [<i>текст</i>]")


async def send_reminder(chat_id: int, user_id: int, username: str, reminder_text: str) -> None:
    await bot.send_message(
        chat_id,
        f"@{html.quote(username)}, напоминаю:\n"
        + f"{html.blockquote(html.quote(reminder_text))}",
    )

    async with aiosqlite.connect('./data/reminders.db') as db:
        await db.execute("DELETE FROM reminders WHERE user_id = ? AND remind_time <= ?", (user_id, datetime.now(),))
        await db.commit()
