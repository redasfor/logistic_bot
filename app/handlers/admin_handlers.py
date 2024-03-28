from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.templates.dao import TemplatesDAO
from app.users.dao import UserDAO
from app.functions.functions import adm_lst
from config import settings

admin_router = Router()


@admin_router.message(Command(commands='stats'))
async def command_stats(msg: Message):
    await msg.delete()
    allowed_user_ids = adm_lst(settings.ADMIN)

    if msg.from_user.id in allowed_user_ids:
        total_templates = await TemplatesDAO.total_rows()
        total_start = await UserDAO.total_rows()
        middle_temp_per_user = round(total_templates / total_start, 1)
        last_temp_added = await TemplatesDAO.max_time()
        count_users_with_templates = await TemplatesDAO.count_users_with_templates()

        await msg.answer(text=f"Стартанули бота: {total_start}\n"
                              f"Всего шаблонов: {total_templates}\n"
                              f"Добавили хотя бы один шаблон: {count_users_with_templates}\n"
                              f"В среднем шаблонов у юзера: {middle_temp_per_user}\n"
                              f"Время и дата добавления последнего шаблона: {last_temp_added['max_1']}")
