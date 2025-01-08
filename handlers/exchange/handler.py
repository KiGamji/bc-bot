import re
import aiohttp
from aiogram import html
from aiogram.types import Message
from aiogram.filters import CommandObject

from .currency_emojis import *
from .default_pairs import *
from .get_pair import *


async def exchange(message: Message, command: CommandObject) -> None:
    args = command.args
    if args:
        args = args.split()
        if len(args) == 2:
            first_currency = args[0].lower()
            second_currency = args[1].lower()
            msg = await message.reply(html.bold('🚀 Получение данных...'))
            rate = await get_pair(f'{first_currency}-{second_currency}')
            if rate:
                rate = parse(rate)
                await msg.edit_text(
                    html.bold(
                        f'{currency_emojis.get(first_currency.upper(), "")} {first_currency.upper()} '
                        f'/ {currency_emojis.get(second_currency.upper(), "")} {second_currency.upper()}: {rate}'
                    )
                )
            else:
                await msg.edit_text(
                    html.bold(
                        '⚠️ Не удалось получить данные. '
                        'Попробуйте позже или проверьте правильность введенных валют.',
                    )
                )
        else:
            await message.reply(
                html.bold('🚫 Укажите две валюты через пробел после команды.')
            )
    else:
        msg = await message.reply(
            html.bold(f'🚀 Получение данных... [0/{len(default_pairs)}]')
        )
        result = ''
        for i, pair in enumerate(default_pairs):
            first_currency, second_currency = pair.split('-')
            msg_pair = pair.upper().replace('-', '/')
            rate = await get_pair(pair)
            if rate:
                rate = parse(rate)
                result += html.bold(
                    f'{currency_emojis.get(first_currency.upper(), "")} {first_currency.upper()} '
                    f'/ {currency_emojis.get(second_currency.upper(), "")} {second_currency.upper()}: {rate}\n'
                )
            else:
                result += html.bold(
                    f'{currency_emojis.get(first_currency.upper(), "")} {first_currency.upper()} '
                    f'/ {currency_emojis.get(second_currency.upper(), "")} {second_currency.upper()}: ⚠️\n'
                )
            await msg.edit_text(
                html.bold(
                    f'🚀 Получение данных... [{i + 1}/{len(default_pairs)}]'
                )
            )
        await msg.edit_text(result)


def parse(rate: str) -> str:
    # Remove thousands separators and strip to two decimal places
    # 12,345.9876 -> 12345.9876
    # 12345.9876 -> 12345.99
    rate = rate.replace(',', '')
    rate = '{:.2f}'.format(float(rate))

    # Convert to russian formatting standard
    # 12345.99 -> 12 345.99
    # 12 345.99 -> 12 345,99
    rate = re.sub(r"(?<=\d)(?=(?:\d{3})+(?:\.\d+))", " ", rate)
    rate = rate.replace('.', ',')

    return rate
