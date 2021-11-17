from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

import asyncio
import aiogram
import logging

from random import randint

logging.basicConfig(level=logging.DEBUG)
Base = declarative_base()

class Verb(Base):
    __tablename__ = "verbs"

    id = sql.Column(sql.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = sql.Column(sql.TIMESTAMP, nullable=False)
    updatet_at = sql.Column(sql.TIMESTAMP, nullable=False)

    verb = sql.Column(sql.String, nullable=False, unique=True)
    
    def __init__(self, verb):
        self.verb = verb
        self.created_at = datetime.utcnow()
        self.updatet_at = datetime.utcnow()

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.verb, self.created_at, self.updatet_at)


engine = sql.create_engine("sqlite:///db.db", echo=True)
Session = sql.orm.sessionmaker(bind=engine)

Base.metadata.create_all(engine)

TOKEN = ""
bot = aiogram.Bot(token=TOKEN)
dp = aiogram.Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message):
    await bot.send_message(chat_id=message.chat.id, text="""
    Привет. Это бот для словесной игры с глаголами на иврите.
    Тебе приходить глагол в форме инфинитива и местоимение, а ты должен придумать вопрос
    с этим глаголом в нужной форме
    
    Команды:
    /play - играть
    /add - добавить глагол в базу
    """)

@dp.message_handler(commands=["add"])
async def add_verb(message):
    last_word = message.text.split()[-1]

    session = Session()
    new_verb = Verb(last_word)
    session.add(new_verb)
    try:
        session.commit()
    except IntegrityError:
        await bot.send_message(chat_id=message.chat.id, text="Такой глагол уже есть, извини")
    else:
        await bot.send_message(chat_id=message.chat.id, text="Глагол добавлен в базу")


@dp.message_handler(commands=["play"])
async def play(message):
    pronouns = ["אֲנִי", "אֲנַחנוּ", "אַתָה", "אַת", "הוּא", "הִיא", "אַתֶם", "אַתֶן", "הֵם", "הֵן"]
    pr_max_ind = len(pronouns) - 1
    pr_id = randint(0, pr_max_ind)
    tenses = ["עבר", "עתיד", "הווה"]
    te_max_ind = len(tenses) - 1
    te_ind = randint(0, te_max_ind) 
    
    session = Session()
    verbs_max_ind = session.query(Verb).count()
    verb_id = randint(1, verbs_max_ind)
    logging.debug(verb_id)
    verb = session.query(Verb).filter_by(id=verb_id).first()
    
    await bot.send_message(chat_id=message.chat.id, text="{} {} {}".format(str(verb.verb), pronouns[pr_id], tenses[te_ind]))


#session = Session()
#verb1 = Verb("ללמוד")
#session.add(verb1)
#session.commit()

if __name__ == "__main__":
    aiogram.executor.start_polling(dp)