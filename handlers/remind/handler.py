import re
from datetime import datetime, timedelta

import aiosqlite
from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject
from aiogram.methods import SetMessageReaction
from aiogram.types import Message, ReactionTypeEmoji

from main import bot
from .parse_time import parse_time
from .scheduler_manager import main_sched


async def remind_command(message: Message, command: CommandObject) -> None:
    args = command.args
    if args:
        args = args.split(' ', 1)
        if len(args) < 2:
            await message.reply(
                "<b>🚫 Использование:</b> /remind [<i>время</i>] [<i>текст</i>]")
            return

        delay, remind_text = args
        delta = parse_time(delay)
        if delta.total_seconds() == 0:
            await message.reply(
                "<b>🚫 Неверный формат времени.\n"
                "Используйте следующие обозначения:</b>\n"
                "– <b>M</b> — для месяцев\n"
                "– <b>w</b> или <b>н</b> — для недель\n"
                "– <b>d</b> или <b>д</b> — для дней\n"
                "– <b>h</b> или <b>ч</b> — для часов\n"
                "– <b>m</b> или <b>м</b> — для минут\n"
                "– <b>s</b> или <b>с</b> — для секунд"
            )
            return

        remind_time = datetime.now() + delta
        # Limit maximum reminder time to 1 year
        limit = datetime.now() + timedelta(days=365)
        if remind_time < limit:
            async with aiosqlite.connect('./data/reminders.db') as db:
                await db.execute(
                    "INSERT INTO reminders (chat_id, user_id, text, time)"
                    "VALUES (?, ?, ?, ?)",
                    (
                        message.chat.id,
                        message.from_user.id,
                        remind_text,
                        remind_time,
                    )
                )
                await db.commit()

            main_sched.add_job(
                send_reminder,
                'date',
                run_date=remind_time,
                args=[
                    message.chat.id,
                    message.from_user.id,
                    remind_text,
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


async def send_reminder(chat_id: int, user_id: int, remind_text: str) -> None:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.user.username is not None:
            name = html.quote(member.user.username)
            mention = f"@{html.quote(name)}"
        else:
            name = html.quote(member.user.first_name)
    except TelegramBadRequest:
        name = user_id  # In worst case, use the user_id
    finally:
        try:
            mention
        except NameError:  # User does not have a username
            mention = f'<a href="tg://user?id={user_id}">{name}</a>'

    await bot.send_message(
        chat_id,
        f"{mention}, напоминаю:\n"
        + f"{html.blockquote(html.quote(remind_text))}",
    )

    async with aiosqlite.connect('./data/reminders.db') as db:
        await db.execute(
            "DELETE FROM reminders WHERE user_id = ? AND time <= ?",
            (user_id, datetime.now(),)
        )
        await db.commit()
