from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = Bot("5309903930:AAEnmmrAKVBvzhtVII5putyBM4QaVJ_KPW8")
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

dp.middleware.setup(LoggingMiddleware())

greet_text = 'Бот считает средний балл по оценкам. Отправьте текстом (через пробел), либо нажимайте по кнопкам'
pattern = 'Оценки: \n{}\nСредний балл: {}'
numbers_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text='2', callback_data='2'),
    InlineKeyboardButton(text='3', callback_data='3'),
    InlineKeyboardButton(text='4', callback_data='4'),
    InlineKeyboardButton(text='5', callback_data='5'),
    InlineKeyboardButton(text='Стереть', callback_data='remove'),
    InlineKeyboardButton(text='', callback_data='none'),
    InlineKeyboardButton(text='Стереть все', callback_data='remove_all')
)


class States(StatesGroup):
    INPUT_GRADES = State()


def clear_input(grades: str):
    grades = " ".join(list(map(lambda x: (x[0]), list(grades.rsplit()))))
    return grades


def get_grades(grades: str):
    return " ".join(grades.rsplit())


def get_average(grades: str):
    grades = list(map(int, grades.rsplit()))
    return round(sum(grades)/len(grades), 2)


async def remove_all(state:FSMContext, msg_to_edit:types.Message):
    await state.update_data(grades='')
    await msg_to_edit.edit_text('Оценки:\n', reply_markup=numbers_kb)


@dp.message_handler(commands=['start', 'help'], state='*')
async def start(message: types.Message, state:FSMContext):
    await message.answer(greet_text)
    user_data = await state.get_data()
    await state.update_data(msg=
                            await message.answer('Оценки:\n', reply_markup=numbers_kb))
    await States.INPUT_GRADES.set()


@dp.message_handler(state=States.INPUT_GRADES)
async def input_grades(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    msg_to_edit = user_data['msg']
    grades = clear_input(message.text)
    await state.update_data(grades=grades)
    await msg_to_edit.edit_text(pattern.format(get_grades(grades), get_average(grades)),
                                parse_mode='Markdown', reply_markup=numbers_kb)

    await message.delete()


@dp.callback_query_handler(state=States.INPUT_GRADES)
async def cb_input_grades(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    msg_to_edit = user_data['msg']
    grades = user_data.get('grades')
    if grades is None:
        grades = ''
    if callback.data not in ('remove', 'remove_all'):
        await state.update_data(grades=f'{grades} {callback.data}')
        grades += ' ' + callback.data
        await msg_to_edit.edit_text(pattern.format(get_grades(grades), get_average(grades)),
                                    reply_markup=numbers_kb)
    elif callback.data == 'remove':
        if len(grades) > 1:
            grades = get_grades(" ".join(grades.rsplit()[:-1]))
            await state.update_data(grades=grades)
            await msg_to_edit.edit_text(pattern.format(get_grades(grades), get_average(grades)),
                                        reply_markup=numbers_kb)
        else:
            await remove_all(state, msg_to_edit)
    else:
        await remove_all(state, msg_to_edit)
    await callback.answer()

executor.start_polling(dispatcher=dp)
