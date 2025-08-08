from aiogram import html
from aiogram.types import CallbackQuery

from handlers.utils import get_mention


async def delete_currency_message(call: CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    username = await get_mention(chat_id, user_id, True)

    await call.message.edit_text(
        f"{call.message.text}"
        "\n\n"
        f"{html.bold('– удалил(-а)')} {username} ({html.code(user_id)})."
    )

    await call.message.delete()
