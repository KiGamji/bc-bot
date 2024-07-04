from datetime import datetime

import aiosqlite

from .handler import send_reminder
from .scheduler_manager import main_sched


class RemindersCron:
    def __init__(self):
        pass

    async def create_database(self) -> None:
        """Create database if not exists."""
        async with aiosqlite.connect('./data/reminders.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    time DATETIME NOT NULL
                )
            ''')
            await db.commit()

    async def restore_reminders(self) -> None:
        """Reschedule reminders from the database on bot startup."""
        async with aiosqlite.connect('./data/reminders.db') as db:
            async with db.execute(
                "SELECT id, chat_id, user_id, text, time FROM reminders"
            ) as cursor:
                async for row in cursor:
                    id, chat_id, user_id, remind_text, remind_time_str = row
                    remind_time = datetime.fromisoformat(remind_time_str)

                    if remind_time <= datetime.now():
                        await send_reminder(chat_id, user_id, remind_text)
                        await db.execute("DELETE FROM reminders WHERE id = ?", (id,))
                        await db.commit()
                    else:
                        main_sched.add_job(
                            send_reminder,
                            'date',
                            run_date=remind_time,
                            args=[
                                chat_id,
                                user_id,
                                remind_text,
                            ],
                        )

    async def run(self) -> None:
        await self.create_database()
        await self.restore_reminders()
