import asyncio
from typing import Any
from parser import pars


async def invert_types(item: str | list[str]):
    async def process_string(value):
        try:
            digit, null = value.split('.')
            if null == '0':
                return int(digit)
            else:
                return float(value)
        except ValueError:
            return int(value)

    if isinstance(item, str):
        return await process_string(item)

    if isinstance(item, list):
        lst = []
        for i in item:
            i = i.replace(',', '.') if ',' in i else i
            lst.append(await invert_types(i))
        return lst


def adm_lst(admin: str):
    if ',' not in admin:
        return [int(admin)]
    else:
        return list(map(int, admin.split(',')))


async def delete_message_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()


async def com(price, commission):
    return price * (commission / 100) if commission else 0


async def log(measure, weight, quantity, logistic_cost, A, B, H):
    # Возвращает числовое значение стоимости логистики
    if measure == 'доллар/кг':
        return ((weight * quantity) / 1_000) * logistic_cost
    total_m3 = (A * B * H * quantity) / 1_000_000
    total_weight_m3 = (weight * quantity) / 1_000_000
    return (total_weight_m3 / total_m3) * logistic_cost


async def total_cost(price, commission, logistic_cost):
    # Использует результаты функций com и log для расчёта итоговой стоимости
    commission_value = await com(price, commission)
    total = price + commission_value + logistic_cost
    return total


async def build_template_info(user_data: dict[str, Any]):
    price = user_data['unit_price'] * user_data['quantity']
    parsers = await pars.currency_conversion(from_val=user_data['payment_currency'], nominal=1)
    total_log = await log(user_data['measure_of_weight'], user_data['weight'], user_data['quantity'],
                          user_data['logistics_cost'], user_data['parameters']['a'],
                          user_data['parameters']['b'], user_data['parameters']['h'])
    total_buyer = await com(price, user_data['commission'])
    USD_to_RUB = await pars.currency_conversion(from_val='USD', nominal=total_log)
    PC_to_RUB = await pars.currency_conversion(from_val=user_data['payment_currency'], nominal=price)
    total = await total_cost(float(PC_to_RUB), user_data['commission'], float(USD_to_RUB))

    result_text = (f"Вот Ваш шаблон:\n\n"
                   f"<b>Название товара:</b> {user_data['product_name']}\n"
                   f"<b>Страна доставки:</b> {user_data['delivery_country']}\n"
                   f"<b>Валюта оплаты:</b> {user_data['payment_currency']}\n"
                   f"<b>Стоимость логистики:</b> {user_data['logistics_cost']} {user_data['measure_of_weight']}\n"
                   f"<b>Цена за единицу товара:</b> {user_data['unit_price']}\n"
                   f"<b>Количество единиц:</b> {user_data['quantity']}\n"
                   f"<b>Параметры см:</b> <b>длина</b> - {user_data['parameters']['a']}, <b>ширина</b> - {user_data['parameters']['b']}, <b>высота</b> - {user_data['parameters']['h']}\n"
                   f"<b>Вес 1 ед товара:</b> {round(user_data['weight'] / 1000, 2)} кг\n"
                   f"<b>Комиссия байера:</b> {user_data['commission']}%\n\n\n"

                   f"<b>Цена товара:</b> {price} {user_data['payment_currency']}   /   {round(float(PC_to_RUB), 2)}₽ по курсу 1{user_data['payment_currency']} = {parsers}\n"
                   f"<b>Цена логистики:</b> {round(float(total_log), 2)}$   /   {round(float(USD_to_RUB), 2)}₽ по курсу 1$ = {await pars.currency_conversion(from_val='USD', nominal=1)}₽\n"
                   f"<b>Комиссия байера:</b> {round(float(total_buyer), 2)} {user_data['payment_currency']}   /   {round(float(await pars.currency_conversion(from_val=user_data['payment_currency'], nominal=total_buyer)), 2)}₽ по курсу 1{user_data['payment_currency']} = {parsers}₽\n"
                   f"<b>Итоговая стоимость:</b> {round(float(total), 2)}₽ при курсах валют выше")

    return result_text
