from decimal import Decimal
from datetime import datetime
from math import ceil

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.functions.functions import invert_types, delete_message_after_delay, build_template_info
from app.keyboards.keyboards import keyboard_delivery_country, keyboard_payment_currency, keyboard_measure_of_weight, \
    keyboard_weight, send_template_page, keyboard_delete, keyboard_create, keyboard_create_and_all_temp, keyboard_main
from app.templates.dao import TemplatesDAO
from app.users.dao import UserDAO
import asyncio

router = Router()
user_dict: dict[int, dict[str, int | str | float | Decimal | dict[str, int | float]]] = {}


class FSMFillForm(StatesGroup):
    product_name = State()
    delivery_country = State()
    payment_currency = State()
    measure_of_weight = State()
    logistics_cost = State()
    unit_price = State()
    quantity = State()
    parameters = State()
    weight = State()
    commission = State()


@router.message(CommandStart(), ~StateFilter(default_state))
async def process_command_start_state(msg: Message, state: FSMContext):
    await msg.delete()  # удаляю команду /старт
    await msg.answer(text='⚙️Вы прервали заполнение шаблона. Данные не были сохранены!\n\n',
                     reply_markup=keyboard_create_and_all_temp,
                     disable_notification=False
                     )
    await state.clear()


# первый старт бота
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(msg: Message):
    await msg.delete()

    # если юзер есть в базе данных
    if await UserDAO.find_one_or_none(telegram_id=msg.from_user.id):
        await msg.answer(text='⚙️Доступные инструменты:\n\n',
                         reply_markup=keyboard_create_and_all_temp
                         )
    else:
        await UserDAO.add(telegram_id=msg.from_user.id, name=msg.from_user.username)
        await msg.answer(text="⚙️Приветствую в нашем бесплатном боте - калькуляторе!\n\n"
                              "Заполни шаблон, ответив на вопросы о товаре, сохрани и посмотри :)\n",
                         reply_markup=keyboard_create
                         )


@router.callback_query(F.data == 'start')
async def back_to_start(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer(text='⚙️Доступные инструменты:\n\n',
                               reply_markup=keyboard_create_and_all_temp
                               )
    await query.answer()


@router.callback_query(F.data == 'create', StateFilter(default_state))
async def start_template_creation(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer(text='Приступим к заполнению шаблона!\n\n'
                                    "Введите название товара:")
    await state.set_state(FSMFillForm.product_name)


@router.message(StateFilter(FSMFillForm.product_name))
async def valid_product_name(msg: Message, state: FSMContext):
    user = await UserDAO.find_one_or_none(telegram_id=msg.from_user.id)
    template = await TemplatesDAO.find_one_or_none(user_id=user.get('id'), product_name=msg.text.strip())
    if not template:
        await state.update_data(product_name=msg.text)
        await msg.answer(text="Выберите страну из которой планируете доставлять товар\n",
                         reply_markup=keyboard_delivery_country)
        await state.set_state(FSMFillForm.delivery_country)
    else:
        err_msg = await msg.answer(text='Шаблон с таким названием уже существует!\n'
                                        'Введите другое название:')
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.callback_query(StateFilter(FSMFillForm.delivery_country), F.data.in_(['Китай', 'Турция', 'Киргизстан']))
async def valid_delivery_country(callback: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_country=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Выберите валюту, в которой будет закупаться товар',
                                  reply_markup=keyboard_payment_currency.as_markup())
    await state.set_state(FSMFillForm.payment_currency)


@router.callback_query(StateFilter(FSMFillForm.payment_currency), F.data.in_(['RUB', 'USD', 'KGS', 'TRY', 'CNY']))
async def valid_payment_currency(callback: CallbackQuery, state: FSMContext):
    await state.update_data(payment_currency=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Выберите единицу измерения',
                                  reply_markup=keyboard_measure_of_weight.as_markup())
    await state.set_state(FSMFillForm.measure_of_weight)


@router.callback_query(StateFilter(FSMFillForm.measure_of_weight), F.data == 'м3')
async def check_callback_measure_m3(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(measure_of_weight='USD')
    await callback.message.answer(
        text='Сколько стоит доставка 1 кубического метра груза у вашего подрядчика? В долларах США')
    await state.set_state(FSMFillForm.logistics_cost)


@router.callback_query(StateFilter(FSMFillForm.measure_of_weight), F.data == 'кг')
async def check_callback_measure_kg(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(measure_of_weight='доллар/кг')
    await callback.message.answer(
        text='Сколько стоит доставка 1кг груза у вашего подрядчика? В долларах США')
    await state.set_state(FSMFillForm.logistics_cost)


@router.message(StateFilter(FSMFillForm.logistics_cost))
async def valid_logistics_cost(msg: Message, state: FSMContext):
    try:
        if not msg.text.startswith('-'):
            num = await invert_types(msg.text.replace(',', '.')) if ',' in msg.text else round(float(msg.text), 2)
            await state.update_data(logistics_cost=num)
            await msg.answer(text='Введите цену за единицу товара')
            await state.set_state(FSMFillForm.unit_price)
        else:
            raise ValueError
    except ValueError:
        user_dict_data = await state.get_data()
        err_msg = await msg.answer(
            text=f"‼️Введено некорректное значение, проверьте правильность ввода стоимости доставки груза и повторите снова‼️\n\n"
                 f"Введите стоимость доставки {user_dict_data.get('measure_of_weight')} груза Вашего подрядчика в долларах США:"
        )
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.unit_price))
async def check_unit_price(msg: Message, state: FSMContext):
    try:
        if not msg.text.startswith('-'):
            num = await invert_types(msg.text.replace(',', '.')) if ',' in msg.text else round(float(msg.text), 2)
            await state.update_data(unit_price=num)
            await msg.answer(text='Введите количество товаров в штуках (не ниже 1ед):')
            await state.set_state(FSMFillForm.quantity)
        else:
            raise ValueError
    except ValueError:
        err_msg = await msg.answer(text='‼️Введено некорректное значение‼️\n'
                                        'Попробуйте еще раз:')
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.quantity),
                lambda x: x.text != '0' and not x.text.startswith('-') and x.text.isdigit())
async def valid_quantity(msg: Message, state: FSMContext):
    num = int(msg.text)
    await state.update_data(quantity=num if num > 0 else 1)
    await msg.answer(text='Введите параметры (сантиметры) в формате "длина*ширина*высота":')
    await state.set_state(FSMFillForm.parameters)


@router.message(StateFilter(FSMFillForm.quantity))
async def invalid_quantity(msg: Message):
    err_msg = await msg.answer(text='‼️Число должно быть целым и больше 0‼️\n\n'
                                    'Попробуйте еще раз:')
    await asyncio.create_task(delete_message_after_delay(err_msg, 4))
    await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.parameters), lambda x: len(x.text.split('*')) == 3)
async def valid_param(msg: Message, state: FSMContext):
    try:
        res = await invert_types(msg.text.split('*'))
        await state.update_data(parameters={"a": res[0],
                                            "b": res[1],
                                            "h": res[2]})

        await msg.answer(text='Введите вес товара в граммах')
        await state.set_state(FSMFillForm.weight)
    except ValueError:
        err_msg = await msg.answer(text='‼️Неверный ввод‼️\n\n'
                                        'Введите корректный формат и повторите попытку!')
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.parameters))
async def invalid_param(msg: Message):
    err_msg = await msg.answer(text='‼️Неверный ввод‼️\n\n'
                                    'Введите корректный формат и повторите попытку!')
    await asyncio.create_task(delete_message_after_delay(err_msg, 4))
    await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.weight), lambda x: x.text.isdigit() and not x.text.startswith('-'))
async def valid_weight(msg: Message, state: FSMContext):
    try:
        await state.update_data(weight=int(msg.text))
        await msg.answer(text='Есть ли комиссия байера?\n\n\n'
                              '✅ Да - введите комиссию в %\n\n'
                              '❌ Нет - введите 0')
        await state.set_state(FSMFillForm.commission)
    except Exception:
        err_msg = await msg.answer(text='‼️Неверный ввод‼️\n\n'
                                        'Введите корректный формат и повторите попытку!')
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.weight))
async def invalid_weight(msg: Message):
    err_msg = await msg.answer(text='‼️Неверный ввод‼️\n\n'
                                    'Введите корректный формат и повторите попытку!')
    await asyncio.create_task(delete_message_after_delay(err_msg, 4))
    await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.commission), lambda x: not x.text.isalpha() and not x.text.startswith('-'))
async def valid_commission(msg: Message, state: FSMContext):
    try:
        num = await invert_types(msg.text.replace(',', '.')) if ',' in msg.text else await invert_types(msg.text)
        await state.update_data(commission=num)
        user_dict[msg.from_user.id] = await state.get_data()
        await state.clear()

        await msg.answer(text='⚙️Отлично! Данные шаблона были сохранены!\n\n',
                         reply_markup=keyboard_weight)
    except ValueError:
        err_msg = await msg.answer(text='‼️Вы вводите неверные значения‼️\n\n'
                                        'Убедитесь в правильности ввода данных и повторите попытку!')
        await asyncio.create_task(delete_message_after_delay(err_msg, 4))
        await msg.delete(time=4)


@router.message(StateFilter(FSMFillForm.commission))
async def invalid_commission(msg: Message):
    err_msg = await msg.answer(text='‼️Вы вводите неверные значения‼️\n\n'
                                    'Убедитесь в правильности ввода данных и повторите попытку!')
    await asyncio.create_task(delete_message_after_delay(err_msg, 4))
    await msg.delete(time=4)


@router.callback_query(F.data == 'show')
async def show_template_command(cb: CallbackQuery):
    await cb.message.delete()
    ID = cb.from_user.id
    user = await UserDAO.find_one_or_none(telegram_id=ID)
    user_id = user.get('id')
    await TemplatesDAO.add(product_name=user_dict[ID]['product_name'],
                           delivery_country=user_dict[ID]['delivery_country'],
                           payment_currency=user_dict[ID]['payment_currency'],
                           logistics_cost=user_dict[ID]['logistics_cost'],
                           measure_of_weight=user_dict[ID]['measure_of_weight'],
                           unit_price=user_dict[ID]['unit_price'],
                           quantity=user_dict[ID]['quantity'],
                           parameters=user_dict[ID]['parameters'],
                           weight=user_dict[ID]['weight'],
                           commission=user_dict[ID]['commission'],
                           user_id=user_id,
                           date=datetime.now()
                           )
    await cb.message.answer(text=await build_template_info(user_data=user_dict[ID]), parse_mode='HTML',
                            reply_markup=keyboard_main)


@router.callback_query(F.data == 'all')
async def get_all_templates(query: CallbackQuery):
    await query.message.delete()
    valid = await UserDAO.find_one_or_none(telegram_id=query.from_user.id)
    all_temp = await TemplatesDAO.find_all(user_id=valid.get('id'))
    if all_temp:
        page = 1
        pages = ceil(len(all_temp) / 5)  # Вычисляем общее количество страниц
        if pages != 0:
            await send_template_page(query.message, all_temp, page, pages)
    else:
        await query.message.answer(text='В настоящий момент у вас нет шаблонов\n',
                                   reply_markup=keyboard_create)


@router.callback_query(lambda x: x.data.startswith("prev_page") or x.data.startswith("next_page"))
async def change_template_page(query: CallbackQuery):
    await query.message.delete()
    callback_data = query.data
    page_change = -1 if callback_data.startswith('prev_page') else 1
    page = int(callback_data.split(":")[1])
    page += page_change
    valid = await UserDAO.find_one_or_none(telegram_id=query.from_user.id)
    if valid:
        all_temp = await TemplatesDAO.find_all(user_id=valid.get('id'))
        pages = ceil(len(all_temp) / 5)
        await send_template_page(query.message, all_temp, page, pages)


@router.callback_query(lambda x: x.data.startswith("template_info:"))
async def template_info_handler(query: CallbackQuery):
    await query.message.delete()
    product_name = query.data.split(':')[-1]

    user = await UserDAO.find_one_or_none(telegram_id=query.from_user.id)
    template = await TemplatesDAO.find_one_or_none(user_id=user.get('id'), product_name=product_name)

    await query.message.answer(text=await build_template_info(template), parse_mode='HTML',
                               reply_markup=keyboard_delete)


@router.callback_query(F.data == 'to_all')
async def again_get_all_templates(query: CallbackQuery):
    await query.answer()
    valid = await UserDAO.find_one_or_none(telegram_id=query.from_user.id)
    all_temp = await TemplatesDAO.find_all(user_id=valid.get('id'))
    page = 1
    pages = ceil(len(all_temp) / 5)  # Вычисляем общее количество страниц
    await send_template_page(query.message, all_temp, page, pages)
    await query.message.delete(time=4)


@router.callback_query(F.data == 'delete')
async def delete_templates(query: CallbackQuery):
    await query.message.delete()
    # Получение product_name и user_id
    product_name = query.message.text.split('\n')[2].split(':')[
        1].strip()  # Убедитесь, что правильно извлекается имя продукта
    user = await UserDAO.find_one_or_none(telegram_id=query.from_user.id)
    was_deleted = await TemplatesDAO.delete_by_names(product_name=product_name, user_id=user.get('id'))
    if was_deleted:
        await query.message.answer(text=f'✅Шаблон "{product_name}" успешно удален!')
    else:
        await query.message.answer(text=f'Шаблон "{product_name}" не найден или уже удален.')

    all_temp = await TemplatesDAO.find_all(user_id=user.get('id'))
    page = 1
    pages = ceil(len(all_temp) / 5)  # Вычисляем общее количество страниц
    if pages != 0:
        await send_template_page(query.message, all_temp, page, pages)
    else:
        await query.message.answer(text='В настоящий момент у вас нет шаблонов\n',
                                   reply_markup=keyboard_create)


@router.message(StateFilter(default_state))
async def echo(msg: Message):
    await msg.delete()
