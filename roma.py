import psycopg2
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

user = 'gen_user'
password = 'tjl?bxq6n-a\l&'
host = '147.45.159.94'
db_name = 'default_db'
port = 5432

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
logging.basicConfig(level=logging.INFO)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class User(Base):
    __tablename__ = "users_table"
    user_id = Column(String, primary_key=True)
    age = Column(String)
    city = Column(String)
    ch_count = Column(String)
    ch_age = Column(String)
    ch_name = Column(String)
    date = Column(String)

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

async def add_users(age, city, count, ch_age, ch_name,user_id,date):
    logging.info("Adding user start")
    query = """
        INSERT INTO users_table (user_id, age, city, ch_count, ch_age, ch_name, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
    cursor = conn.cursor()
    conn.autocommit = True
    try:
        cursor.execute(query, (user_id, age, city, count, ch_age, ch_name, date))
        logging.info("User added")
    except psycopg2.errors.DuplicateDatabase:
        logging.info("fail")

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

async def remove_user_from_db(user_id):
    logging.info("start removing")
    conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
    cursor = conn.cursor()
    query = f"""
        DELETE FROM users_table WHERE user_id = %s
        """
    cursor.execute(query, (str(user_id),))
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("end removing")

async def scan_db(user_id, age, city, count, children_age, children_name, date):
    records = await get_users()
    for record in records:
        if record[0] == str(user_id):
            logging.info("user in db")
            await replace_date(user_id)
            return
    await add_users(age, city, count, children_age, children_name, user_id, date)
    logging.info("user add")

async def replace_date(user_id):
    conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM users_table WHERE user_id = %s", (user_id,))
    oldDate = cursor.fetchall()[0][0]
    logging.info('oldData = '+oldDate)
    query = f"""
                    UPDATE users_table
                    SET date = %s
                    WHERE user_id = %s;
                            """
    month = oldDate[5:7]
    day = oldDate[8:10]
    year = oldDate[:4]
    new_date_str = f'{int(year) + (int(month) // 12)}-{(int(month) % 12 + 1):02}-{day:02}'
    logging.info("newData = " + new_date_str)
    cursor.execute(query, (new_date_str, user_id))
    conn.commit()
    cursor.close()
    conn.close()