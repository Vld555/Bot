from aiogram import Bot, Dispatcher, types, F
import asyncio
import re
import re
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import logging
import psycopg2
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

bot = Bot('7241170836:AAEErcqq6XmFmPA0_1lL2dUCE8ibuiFg-FY')
dp=Dispatcher()
logging.basicConfig(level=logging.INFO)
user = 'postgres'
password = 'vlad'
host = 'db'
db_name = 'postgres'
port = 5432

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
logging.basicConfig(level=logging.INFO)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class User(Base):
    __tablename__ = "users_table"
    user_id = Column(String, primary_key=True)
    name = Column(String)
    age = Column(String)
    number= Column(String)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def create_db():
    conn = psycopg2.connect(host=host, port=port, database="postgres", user=user, password=password)
    cursor = conn.cursor()
    conn.autocommit = True
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print("База данных успешно создана")
    except psycopg2.errors.DuplicateDatabase:
        print("База данных уже существует")

    cursor.close()
    conn.close()

async def add_users(user_id, name, age, number):
    logging.info("Adding user start")
    query = """
        INSERT INTO users_table (user_id, name, age, number)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET name = EXCLUDED.name, age = EXCLUDED.age, number = EXCLUDED.number
        """
    conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
    cursor = conn.cursor()
    conn.autocommit = True
    try:
        cursor.execute(query, (user_id, name, age, number))
        logging.info("User added")
    except psycopg2.Error as e:
        logging.error(f"Error adding or updating user: {e}")

    cursor.close()
    conn.close()

async def get_users():
    conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_table")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records


class Form(StatesGroup):
    name = State()
    number = State()
    age = State()
    apply = State()

class Form2(StatesGroup):
    question = State()
    city = State()

@dp.message(Command('start'))
async def start(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text = 'Задать вопрос'))
    await message.answer('Привет, введите /register, чтобы начать регистрацию \
/help, чтобы получить дополнительную информацию или задайте вопрос',reply_markup=builder.as_markup(resize_keyboard = True))

@dp.message(F.text.lower()=='задать вопрос')
async def questions(message:Message,state: FSMContext):
    await message.answer('Введите ваш вопрос')
    await state.set_state(Form2.question)

@dp.message(Form2.question)
async def ask_question(message:Message,state:FSMContext):
    await state.update_data(question = message.text)
    await message.answer('Введите ваш город')
    await state.set_state(Form2.city)

admin_id = '964963032'
@dp.message(Form2.city)
async def set_city(message:Message, state:FSMContext):
    await state.update_data(city = message.text)
    await message.answer('Ваш вопрос был отправлен администратору\n\
 /start - вернуться в главное меню')
    question_data = await state.get_data()
    await bot.send_message(admin_id,f"Пользователь {message.from_user.id}\nВопрос: {question_data['question']}\n\
Город: {question_data['city']}")
    await state.clear()

    



@dp.message(Command("register"))
async def register(message: Message, state: FSMContext):
    await message.answer("Введите имя и фамилию")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def set_name(message:Message, state: FSMContext):
    if message.text.count(' ')!=1 or any(ch.isdigit() for ch in message.text):
        await message.answer('Неверный ввод, повторите попытку...')
        return
    await state.update_data(name = message.text)
    await state.set_state(Form.age)
    await message.answer('Укажите ваш возраст')

@dp.message(Form.age)
async def set_age(message:Message, state = FSMContext):
    if not(message.text.isdigit()) or int(message.text)<=0 or int(message.text)>120:
        await message.answer('Пожалуйста, введите ваш настоящий возраст...')
        return
    await state.update_data(age = message.text)
    await state.set_state(Form.number.state)
    await message.answer('Введите номер телефона')

@dp.message(Form.number)
async def set_number(message:Message, state:FSMContext):
    if not(re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text)):
        await message.answer('Неверный ввод номера телефона, повторите попытку...')
        return
    await state.update_data(number=message.text)
    user_data = await state.get_data()
    await message.answer(f"Проверьте введенные данные:\nВаше имя: {user_data['name']}\n\
Ваш возраст: {user_data['age']}\nВаш номер телефона: {user_data['number']}")
    await state.set_state(Form.apply.state)
    await message.answer('Введите Подтвердить, если вы подтверждаете ввод')

@dp.message(Form.apply)
async def set_apply(message:Message,state:FSMContext):
    if message.text!='Подтвердить':
        await state.clear()
        await message.answer("Давайте начнем регистрацию заново. Введите имя и фамилию")
        await state.set_state(Form.name)
        return
    user_data = await state.get_data()

    await add_users(message.from_user.id, user_data['name'], user_data['age'], user_data['number'])

    await message.answer('Вы подтвердили данные\nВведите /profile, чтобы увидеть личную информацию')
    await state.clear()

@dp.message(Command('profile'))
async def profile (message:Message):
    users = await get_users()
    if users:
        user_found = False
        for user in users:
            if user[0] == str(message.from_user.id):
                await message.answer(f"Ваш профиль:\nИмя: {user[1]}\nВозраст: {user[2]}\nТелефон: {user[3]}\n\
/start - вернуться в главное меню")
                user_found = True
                break
        if not user_found:
            await message.answer("Вы еще не зарегистрированы. Используйте команду /register для регистрации.")
    else:
        await message.answer("Вы еще не зарегистрированы. Используйте команду /register для регистрации.")
@dp.message(Command('help'))
async def help(message: Message):
    await message.answer('Привет! это бот, позволяющий занести свои данные в базу\n\
Введи /register, чтобы начать регистрацию\n\
/profile, чтобы получить личные данные')
async def main():
    logging.info("бот запущен")
    logging.info("Ожидание готовности базы данных...")
    await asyncio.sleep(10)  # Ждем 10 секунд
    try:
        create_db()
        await create_tables()
    except Exception as e:
        logging.info(f"Ошибка при подключении к базе данных: {e}")
        raise
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())