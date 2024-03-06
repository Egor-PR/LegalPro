from aiogram import Router
from aiogram.types import Message

echo_router = Router(name=__name__)


@echo_router.message()
async def echo_handler(message: Message, user: dict | None) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        # await message.send_copy(chat_id=message.chat.id)
        await message.reply(str(user))
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer('Nice try!')




