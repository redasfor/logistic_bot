from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

keyboard_delivery_country = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Китай", callback_data="Китай"),
            InlineKeyboardButton(text="Турция", callback_data="Турция"),
            InlineKeyboardButton(text="Киргизстан", callback_data="Киргизстан"),
        ]
    ]
)

keyboard_payment_currency = InlineKeyboardBuilder()
keyboard_payment_currency.row(
    InlineKeyboardButton(text="Российский рубль", callback_data="RUB"),
    InlineKeyboardButton(text="Американский доллар", callback_data="USD"),
)
keyboard_payment_currency.row(
    InlineKeyboardButton(text="Киргизский сом", callback_data="KGS"),
    InlineKeyboardButton(text="Турецкая лира", callback_data="TRY"),
)
keyboard_payment_currency.row(
    InlineKeyboardButton(text="Китайский юань", callback_data="CNY")
)

keyboard_measure_of_weight = InlineKeyboardBuilder()
keyboard_measure_of_weight.row(
    InlineKeyboardButton(text="кг/м3", callback_data="м3"),
    InlineKeyboardButton(text="Доллар/кг", callback_data="кг"),
)

keyboard_yes_or_no = InlineKeyboardBuilder()
keyboard_yes_or_no.row(InlineKeyboardButton(text="Да", callback_data="yes"))
keyboard_yes_or_no.row(InlineKeyboardButton(text="Нет", callback_data="no"))

keyboard_weight = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Посмотреть", callback_data="show")]]
)

keyboard_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🗑Удалить", callback_data="delete")],
        [InlineKeyboardButton(text="◀️Назад", callback_data="to_all")],
    ]
)

keyboard_create = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать новый шаблон", callback_data="create")]
    ]
)

keyboard_create_and_all_temp = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать новый шаблон", callback_data="create")],
        [InlineKeyboardButton(text="Мои шаблоны", callback_data="all")],
    ]
)

keyboard_main = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]]
)


async def send_template_page(msg, all_temp, page, pages):
    start_index = (page - 1) * 5
    end_index = start_index + 5
    templates_on_page = all_temp[start_index:end_index]

    buttons = [
        InlineKeyboardButton(
            text=tmp["product_name"],
            callback_data=f"template_info:{tmp['product_name']}",
        )
        for tmp in templates_on_page
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for btn in buttons:
        keyboard.inline_keyboard.append([btn])

    if pages >= 1:
        navigation_buttons = []
        if page == 1 or page == pages:
            navigation_buttons.append(
                InlineKeyboardButton(text="Главная", callback_data="start")
            )
        if page > 1:
            navigation_buttons.append(
                InlineKeyboardButton(text="◀️Назад", callback_data=f"prev_page:{page}")
            )
        if page < pages:
            navigation_buttons.append(
                InlineKeyboardButton(text="Вперед▶️", callback_data=f"next_page:{page}")
            )

        keyboard.inline_keyboard.append(navigation_buttons)
    await msg.answer(text=f"Выберите шаблон (страница {page}/{pages}):", reply_markup=keyboard)
