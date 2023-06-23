import pycountry
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import IAM_TOKEN, TOKEN_API, folder_id
from keyboards import ikb, ikb2
from languages import languages

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

HELP_COMMAND = """
• /start - начало работы с ботом
• /help - информация о командах бота
• /languages - список поддерживаемых языков
"""


class FastMessage(StatesGroup):
    choice1 = State()
    choice2 = State()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_COMMAND)
    await message.delete()


@dp.message_handler(commands=['languages'])
async def languages_command(message: types.Message):
    await message.answer(text=languages)
    await message.delete()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Привет! Рады тебя видеть.')
    await message.answer(text='Для начала работы напиши то,'
                         'что хочешь перевести!')
    await message.delete()


@dp.message_handler(state=FastMessage.choice1)
async def lng_choice(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите язык, на который переводить',
                           reply_markup=ikb
                           )
    await FastMessage.next()


@dp.callback_query_handler(state=FastMessage.choice2)
async def translate(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'True':
        await callback.bot.send_message(chat_id=callback.from_user.id,
                                        text='Выберите язык, на который переводить',
                                        reply_markup=ikb)
        await callback.message.edit_reply_markup()
    elif callback.data == 'False':
        await callback.answer('Вы закончили перевод')
        await callback.message.edit_reply_markup()
        await state.finish()
        return

    if len(callback.data) < 3:
        await callback.message.edit_reply_markup()
        async with state.proxy() as data:
            data['lng'] = callback.data
            print(data)
        body = {
            "targetLanguageCode": data['lng'],
            "texts": data['text'],
            "folderId": folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(IAM_TOKEN)
        }

        response = requests.post('https://translate.api.cloud.yandex.net/'
                                 'translate/v2/translate',
                                 json=body,
                                 headers=headers).json()
        print(response)
        text = response['translations'][0].get('text')
        language = pycountry.languages.get(alpha_2=data['lng'].upper())
        print(language, data['lng'].upper())
        await callback.message.answer(text='Переведено на: ' + language.name)
        await callback.message.answer(text='Перевод: ' + text,
                                      reply_markup=ikb2)
        print(callback.data)


@dp.message_handler()
async def all_messages(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        print(data)
    await message.answer('Выбери язык, на который переводить',
                         reply_markup=ikb)
    await FastMessage.choice2.set()

if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True)
