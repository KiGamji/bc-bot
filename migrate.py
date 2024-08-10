import asyncio
import os
import shutil

import aiosqlite
from dotenv import load_dotenv

load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")
if CHAT_ID == "" or None:
    print("Please fill the .env from .env.example first.")
    exit(1)


async def main():
    v3_to_v4 = await check_v3_to_v4()
    if v3_to_v4:
        print("Done! If there were no errors, you can now remove the 'static' folder and run the bot.")
    else:
        print("'static' folder is missing. Perhaps you have already migrated?")


async def check_v3_to_v4():
    run_dir = os.path.dirname(os.path.realpath(__file__))
    static_dir = os.path.join(run_dir, 'static')
    if os.path.exists(static_dir):
        print("Found v3 files. Start migrating to v4.")
        await v3_to_v4()
        return True
    else:
        return False


async def v3_to_v4():
    run_dir = os.path.dirname(os.path.realpath(__file__))
    static_dir = os.path.join(run_dir, 'static')
    data_dir = os.path.join(run_dir, 'data')

    # static -> data
    shutil.copytree(static_dir, data_dir, dirs_exist_ok=True)

    # Update older databases for compatibility with new versions.
    # msg_stats (messages): Adds 'chat_id' column and assigns it to 'CHAT_ID' for old entries.
    async with aiosqlite.connect('./data/msg_stats.db') as db:
        await db.execute('ALTER TABLE messages ADD COLUMN chat_id INTEGER')
        await db.commit()

        await db.execute('''
            UPDATE messages SET chat_id = ?
            WHERE chat_id IS NULL
        ''', (CHAT_ID,))
        await db.commit()

    # reminders: Drops the 'username' column, and renames 'remind_time' column to 'time'.
    async with aiosqlite.connect('./data/reminders.db') as db:
        await db.execute('ALTER TABLE reminders DROP COLUMN username')
        await db.commit()

        await db.execute('''
           ALTER TABLE reminders
           RENAME COLUMN remind_time to time
        ''')
        await db.commit()


if __name__ == '__main__':
    asyncio.run(main())
