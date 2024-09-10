import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from app import keyboards as kb
from GPT import gpt

TOKEN = "YOUR_TOKEN"
bot = Bot(TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class PersonState(StatesGroup):
    waiting_description = State()
    chatting = State()


def create_table():

    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS ChatGPT (
                    id INT,
                    personality TEXT,
                    con TEXT,
                    con2 TEXT
                    )""")
    connect.commit()
    connect.close()


@dp.message_handler(lambda message: message.text == "В главное меню")
@dp.message_handler(commands="start")
async def start(message: Message) -> None:

    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM ChatGPT WHERE id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    if not user:  # Проверка пользователя в бд, если нету добавляем
        cursor.execute(
            "INSERT INTO ChatGPT VALUES (?, ?, ?, ?)", (message.from_user.id, "", "", "")
        )

    # Приветствие пользователя
    await message.answer("Привет! Я личный помощник Helpus.\nПриступим🔥", reply_markup=kb.main_board, )

    connect.commit()
    connect.close()


@dp.message_handler(commands="reset")
async def reset(message: Message) -> None:

    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute(
        "UPDATE ChatGPT SET con = ?, con2 = ?, personality = ? WHERE id = ?",
        ("", "", "", message.chat.id)
    )
    cursor.fetchone()
    connect.commit()
    connect.close()

    await message.answer("✅Личность и история диалога отчищена✅")


@dp.message_handler(commands="person")
async def com_person(message: types.Message, state: FSMContext):
    await message.answer(text="Опишите своего личного помошника.\nПример: Кто он и чем он должен заниматься")
    await PersonState.waiting_description.set()


@dp.message_handler(state=PersonState.waiting_description)
async def person(message: types.Message, state: FSMContext) -> None:
    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute(
        "UPDATE ChatGPT SET personality = ? WHERE id = ?", (message.text, message.from_user.id)
    )

    connect.commit()
    connect.close()

    await state.finish()
    await message.answer(text="Ваш помощник:\n" + message.text)


@dp.message_handler(commands='info')
async def information(message: types.Message) -> None:
    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute(
        "SELECT personality FROM ChatGPT WHERE id = ?", (message.chat.id,)
    )

    person_info = cursor.fetchone()[0]

    connect.close()
    if person_info != "":
        await message.answer(text="Ваш помощник:\n" + person_info)
    else:
        await message.answer(text="Ваш помощник не указан!")


@dp.message_handler(commands="generate")
async def start_chat(message: types.Message, state: FSMContext):
    connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
    cursor = connect.cursor()

    cursor.execute(
        "SELECT personality FROM ChatGPT WHERE id = ?", (message.chat.id,)
    )

    person_info = cursor.fetchone()[0]

    if person_info != '':
        await state.set_state(PersonState.chatting.state)
    else:
        await message.answer(text="Вы не указали личность ващего помощника!")


@dp.message_handler(state=PersonState.chatting)
async def chat(message: types.Message, state: FSMContext) -> None:
    if message.text != 'В главное меню':
        msg_accept = await message.answer(text="Генерация ♻️")
        gpt_answer = await gpt(text=message.text, user_id=message.from_user.id)
        if not gpt_answer:
            await msg_accept.edit_text(
                text="❌ Что-то пошло не так. Попробуй снова через 30 секунд"
            )
            return
        await msg_accept.delete()
        await message.answer(text=gpt_answer, reply_markup=kb.exit_board)
    else:
        exit_chat = await message.answer(message.text, reply_markup=types.ReplyKeyboardRemove())
        await exit_chat.delete()
        await state.finish()
        await start(message)


@dp.callback_query_handler()
async def callback_query_keyboard(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'start':
        await start_chat(callback.message, state)
    elif callback.data == 'com_person':
        await com_person(callback.message, state)
    elif callback.data == 'info':
        await information(callback.message)
    elif callback.data == 'reset':
        await reset(callback.message)
    await callback.answer()


if __name__ == "__main__":
    create_table()
    executor.start_polling(dp, skip_updates=True, allowed_updates=[])
