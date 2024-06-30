from datetime import datetime

from aiogram import Bot,Dispatcher,types
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from dateutil.relativedelta import relativedelta
import re
import re
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

TOKEN_API = '7007442319:AAFia58P8WwKSJABnGizTNbWtQZKx5TVwyU'
CHAT_ID = -1002075260879
bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    number = State()
    comment = State()
    apply = State()

# async def remove_users():
#     record = "2024-06-21"
#     now = datetime.now()
#     logging.info(now + relativedelta(months=+1))
#     current_date = now.date()
#     logging.info("cur date: " + str(current_date))
#     start_date_obj = datetime.strptime(str(record)[:10], '%Y-%m-%d')
#     logging.info(start_date_obj)
#     end_date_obj = start_date_obj + relativedelta(months=+1)
#     logging.info("end date: " + str(end_date_obj))
#     dateNow = datetime.strptime(str(current_date)[:10], '%Y-%m-%d')
#     dateOst = end_date_obj - dateNow
#     logging.info(dateOst.days==30)
#
#     if dateOst.days == 1:
#         await bot.send_message(record[0], "До окончания подписки остался 1 день")
#     elif dateOst.days == 3:
#         await bot.send_message(record[0], "До окончания подписки осталось 3 дня")
#     elif dateOst.days == 5:
#         await bot.send_message(record[0], "До окончания подписки осталось 5 дней")
#     if dateNow >= end_date_obj:
#         await bot.send_message(record[0], "Подписка закончилась")


# @dp.message()
# async def start(message: Message):
#     # await message.answer(text=f"{message.from_user.first_name}, Добро пожаловать в компанию DamnIT")
#     pattern = r'^[a-zA-Zа-яА-Я\s]+$'
#     if message.text.lower().count('а') + message.text.lower().count('a') != 0 or not re.match(pattern, message.text):
#         await bot.ban_chat_member(chat_id=CHAT_ID, user_id=message.from_user.id)
#         await bot.send_message(CHAT_ID, message.from_user.first_name + "был забанен за букву АААААА")
#     # await state.set_state(Form.name.state)

@dp.message(state=Form.name)
async def set_name(message: Message, state: FSMContext):
    if message.text.count(' ') != 2 or any(ch.isdigit() for ch in message.text):
        await message.answer("Введено некорректрое ФИО. Пожалуйста повторите ввод")
        return
    await state.update_data(name = message.text)
    await state.set_state(Form.number.state)
    await message.answer("Укажите Ваш номер телефона")

@dp.message(state=Form.number)
async def set_number(message: Message, state: FSMContext):
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text)
    if not result:
        await message.answer("Введенный номер телефона некорректен. Пожалуйста повторите ввод")
        return
    await state.update_data(number=message.text)
    await state.set_state(Form.comment.state)
    await message.answer("Напишите любой комментарий")

@dp.message(state=Form.comment)
async def set_comm(message: Message, state: FSMContext):
    await state.update_data(comment = message.text)
    await message.answer("Последний шаг! Ознакомься с вводными положениями")
    await bot.send_document(message.chat.id,document=open("test.pdf","rb"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Да")
    await message.answer("Ознакомился?", reply_markup=keyboard)
    await state.set_state(Form.apply.state)


@dp.message(state=Form.apply)
async def set_apply(message: Message, state: FSMContext):
    if message.text != "Да":
        await message.answer("Пожалуйста нажмите на кномку принять, если Вы ознакомились.")
        return
    await message.answer("Спасибо за успешную регистрацию",reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(message.chat.id, photo=open("photo.jpg", "rb"))
    data = await state.get_data()
    await bot.send_message("6262559451", f"Пришла новая информация от {message.from_user.username}\n\
ФИО: {data['name']}\nТелефон: {data['number']}\nКомментарий: {data['comment']}")
    await state.finish()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())