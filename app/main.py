from aiogram import Bot, Dispatcher
import asyncio

from app.handlers import router


bot = Bot(token="6969902730:AAFQqgRN9CBvV5NfIBPt_01wGY3yNXf5cFc")
dp=Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot выключен')