from aiogram import Bot, Dispatcher, types, F
import asyncio
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import logging


logging.basicConfig(level=logging.INFO)
bot = Bot(token="6969902730:AAFQqgRN9CBvV5NfIBPt_01wGY3yNXf5cFc")
dp = Dispatcher()



@dp.message(Command('start'))
async def start(message: Message):
    await message.answer('привет')
    # kb = [[KeyboardButton(text='каталог'), KeyboardButton(text='цены')],
    #        [KeyboardButton(text='контакты')]]
    # keyboard = ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
    # await message.answer('Ознакомьтесь с информацией', reply_markup=keyboard)
    #второй способ reply кнопок
    # builder = ReplyKeyboardBuilder()
    # mas = ['Контакты','Цены','Привет','Пока','Ознакомиться']
    # for i in mas:
    #     builder.add(KeyboardButton(text=i))
    # builder.adjust(1,2)
    # await message.answer('Ознакомьтесь',reply_markup=builder.as_markup())
    builder = InlineKeyboardBuilder()
    mas = ['ABOBA']
    for i in mas:
        builder.add(InlineKeyboardButton(text=i,callback_data='hi'))
    await message.answer('Ознакомьтесь',reply_markup=builder.as_markup())

@dp.callback_query(F.data=='hi')
async def aa(callback: CallbackQuery):
    await callback.message.answer('Ты даун')


@dp.message(F.text.lower()=='как дела')
async def hy(message: Message):
    await message.reply('У меня все хорошо, а у вас?')
    #await bot.send_message('6262559451','козел')
# @dp.message()
# async def aaa(message: Message):
#     await message.answer(message.text)



async def main():
    logging.info("бот запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())