import asyncio
from sys import platform

from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import *
from static.tokens import *

bcID = -1001474397357
bcMessageFilter = F.chat.id == bcID
bcCallbackFilter = F.message.chat.id == bcID

bot = Bot(
    TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

scheduler = AsyncIOScheduler()


async def main():
    dp.message.register(start, CommandStart(), bcMessageFilter)
    dp.message.register(start, Command("help"), bcMessageFilter)

    dp.message.register(alo, Command("alo"))
    dp.message.register(cum, Command("cum"))
    dp.message.register(exchange, Command("exchange"), bcMessageFilter)
    dp.message.register(layout_command, Command("layout"), bcMessageFilter)
    dp.message.register(remind_command, Command("remind"), bcMessageFilter)
    dp.message.register(stats_command, Command("stats"), bcMessageFilter)

    @dp.callback_query(F.data.in_({'day', 'week', 'month'}) & bcCallbackFilter)
    async def stats_callback_(call: CallbackQuery) -> None:
        await stats_callback(call)

    @dp.callback_query(bcCallbackFilter & F.data == 'delete')
    async def delete_currency_message_(call: CallbackQuery) -> None:
        await delete_currency_message(call)

    @dp.message(bcMessageFilter)
    async def non_command(message: Message) -> None:
        stats = Stats()
        await stats.log(message)
        await convert_currency(message)

    reminders_cron = RemindersCron()
    await reminders_cron.run()

    stats_cron = StatsCron()
    await stats_cron.run()
    scheduler.add_job(
        stats_cron.run,
        trigger='interval',
        days=1,
    )

    scheduler.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    if platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
