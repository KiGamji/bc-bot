import re
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from .currency_emojis import *
from .currency_triggers import *
from .get_rates import *
from .main_currencies import *


def preprocess_message(message: str) -> str:
    # Remove mentions
    message = re.sub(r"@(\S+)", "", message)
    # Remove URLs
    message = re.sub(
        r"\b(?:https?:\/\/|www\.)\S+\b|\b\S+\.com\S*\b", "", message,
    )
    # Remove spaces within numbers
    message = re.sub(
        r"(?<!\d)(\d{1,3}(?: \d{3})*(?:\.\d+)?)(?=(?:\s\d{3})*(?:\.\d+)?|\D|$)",
        lambda match: match.group(1).replace(" ", ""),
        message,
    )
    # Remove lines that contain Java log references with $
    message = re.sub(
        r"^\s*at\b.*\b\w+\$\w+.*$", "", message, flags=re.MULTILINE,
    )

    return message


async def convert_currency(message: Message) -> None:
    if not message.text:
        return
    text = preprocess_message(message.text.lower())
    response = ''
    processed_amounts = set()

    # Sort currency triggers by the number of words in descending order
    sorted_triggers = sorted(currency_triggers.items(),
                             key=lambda x: -len(x[0]))

    # Find all matches of currency triggers in the message
    matches = []
    for trigger_words, currency_code in sorted_triggers:
        trigger_regex = r'\s*'.join([re.escape(word)
                                    for word in trigger_words])
        for match in re.finditer(trigger_regex, text):
            start_index = match.start()
            end_index = match.end()
            amount = None

            # Check if there is a number before the currency trigger
            if start_index > 0:
                pre_match = text[:start_index].rstrip()
                pre_match_number = re.search(
                    r'(\d[\d\s]*[.,])?\d+\s*$', pre_match)
                if pre_match_number:
                    amount = float(pre_match_number.group().replace(',', '.'))
                    start_index = pre_match_number.start()

            # Check if there is a number after the currency trigger
            if amount is None and end_index < len(text):
                post_match = text[end_index:].lstrip()
                post_match_number = re.search(
                    r'^\s*(\d[\d\s]*[.,])?\d+', post_match)
                if post_match_number:
                    amount = float(post_match_number.group().replace(',', '.'))
                    end_index += post_match_number.end()

            # If a number was found before or after the currency trigger
            if amount is not None:
                matches.append((currency_code, amount, start_index, end_index))

    # Sort matches by their start index in ascending order
    matches.sort(key=lambda x: x[2])

    # Process matches
    for currency_code, amount, start_index, end_index in matches:
        if (currency_code, amount) not in processed_amounts:
            processed_amounts.add((currency_code, amount))
            rates = await get_rates(currency_code)
            if rates is not None:
                response += f'{currency_emojis.get(currency_code, "")}{amount:.2f} {currency_code}:\n\n'
                for currency in main_currencies:
                    if currency != currency_code:
                        rate = rates[currency]
                        response += f'{currency_emojis.get(currency, "")}{rate * amount:.2f} {currency}\n'
                response += '—————\n'

    # Send response
    if response:
        response = re.sub(r"(?<=\d)(?=(?:\d{3})+(?:\.\d+))", " ", response)
        response = response.replace('.', ',')
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Удалить", callback_data='delete')],
            ]
        )
        await message.answer(
            response.strip().rstrip('—————').strip(),
            reply_markup=reply_markup,
        )
