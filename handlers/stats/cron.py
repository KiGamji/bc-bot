from datetime import datetime, timedelta

import aiosqlite


class StatsCron:
    def __init__(self):
        pass

    async def run(self) -> None:
        await self._create_database()
        await self._delete_old_records()

    async def _create_database(self) -> None:
        """Create database if not exists."""
        async with aiosqlite.connect('./data/msg_stats.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    timestamp TEXT
                )
            ''')
            await db.commit()

    async def _delete_old_records(self) -> None:
        """Remove database records older than one month."""
        month_ago = datetime.now() - timedelta(days=30)
        date_str = month_ago.strftime('%Y-%m-%d %H:%M:%S')

        async with aiosqlite.connect('./data/msg_stats.db') as db:
            await db.execute('''
                DELETE FROM messages
                WHERE timestamp < ?
            ''', (date_str,)
            )
            await db.commit()

            await db.execute('VACUUM')
            await db.commit()
