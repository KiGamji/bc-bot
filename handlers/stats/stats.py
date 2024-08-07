from datetime import datetime, timedelta

import aiosqlite
from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


class Stats:
    def __init__(self):
        pass

    async def get(self, *args):
        response = await self._process_message(*args)
        return response

    async def log(self, *args):
        response = await self._log_message(*args)
        return response

    def _get_reply_markup(self, day=False, week=False, month=False):
        buttons = []
        if day:
            buttons.append(InlineKeyboardButton(text="🕒 За день", callback_data='day'))
        if week:
            buttons.append(InlineKeyboardButton(text="🕒 За неделю", callback_data='week'))
        if month:
            buttons.append(InlineKeyboardButton(text="🕒 За месяц", callback_data='month'))

        return InlineKeyboardMarkup(inline_keyboard=[buttons])

    async def _get_stats(
            self, chat_id: int, days: int, users_limit: int) -> tuple:
        async with aiosqlite.connect('./data/msg_stats.db') as db:
            now = datetime.utcnow()
            time = (now - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

            cursor = await db.execute('''
                SELECT user_id, COUNT(*) AS msg_count FROM messages
                WHERE chat_id = ? AND timestamp > ?
                GROUP BY user_id ORDER BY msg_count DESC LIMIT ?
                ''',
                (chat_id, time, users_limit)
            )
            stats = zip(*await cursor.fetchall())

            cursor = await db.execute(
                'SELECT COUNT(*) FROM messages WHERE chat_id = ? AND timestamp > ?',
                (chat_id, time)
            )
            total = (await cursor.fetchone())[0]

            return stats, total

    async def _log_message(self, message: Message) -> None:
        chat_id = message.chat.id
        user_id = message.from_user.id
        timestamp = message.date.strftime('%Y-%m-%d %H:%M:%S')

        async with aiosqlite.connect('./data/msg_stats.db') as db:
            await db.execute(
                'INSERT INTO messages (chat_id, user_id, timestamp) VALUES (?, ?, ?)',
                (chat_id, user_id, timestamp),
            )
            await db.commit()

    async def _process_list(
            self, chat_id: int, days: int, message: Message) -> tuple:
        # 10 users by default
        stats = await self._get_stats(chat_id, days, 10)
        stats_list = []
        total = stats[1]

        try:
            ids, counts = stats[0]
        except ValueError:
            stats_list.append(
                html.italic("Ой, здесь ничего нет!")
                + "\n"
                + "Нет данных за выбранный период."
            )
            return stats_list, total

        names = []
        for user_id in ids:
            try:
                user = await message.bot.get_chat_member(chat_id, user_id)
                names.append(user.user.full_name)
            # Doesn't work rarely for some reason, append user_id instead
            except TelegramBadRequest:
                names.append(user_id)

        for position, (name, user_id, msg_count) in enumerate(zip(names, ids, counts), 1):
            if isinstance(name, str):
                stats_list.append(
                    f"{position}. "
                    + html.link(
                        html.quote(name),
                        f"tg://openmessage?user_id={user_id}"
                    )
                    + f" – {msg_count}"
                )
            else:
                stats_list.append(
                    f"{position}. "
                    + html.code(name)
                    + f" – {msg_count}"
                )

        return stats_list, total

    async def _process_message(
            self, message: Message, call: CallbackQuery) -> tuple:
        chat_id = message.chat.id if message else call.message.chat.id

        # 1 day by default
        days = 1
        period = "день"

        reply_markup = self._get_reply_markup(week=True, month=True)

        if call:
            if call.data == 'week':
                days = 7
                period = "неделю"
                reply_markup = self._get_reply_markup(day=True, month=True)
            elif call.data == 'month':
                days = 30
                period = "месяц"
                reply_markup = self._get_reply_markup(day=True, week=True)

            stats = await self._process_list(chat_id, days, call.message)
        else:
            stats = await self._process_list(chat_id, days, message)

        message_list = "\n".join(stats[0])
        total = "".join(str(stats[1]))

        stats_message = (
            f"<b>📊 Сообщения за {period}</b>"
            + "\n\n"
            + f"{message_list}"
            + "\n\n"
            + f"<b>Всего сообщений — {total}</b>"
        )

        return stats_message, reply_markup
