from app.users.models import Users
from app.dao.base import BaseDAO


class UserDAO(BaseDAO):
    model = Users
