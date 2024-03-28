from app.dao.base import BaseDAO
from app.templates.models import Templates


class TemplatesDAO(BaseDAO):
    model = Templates
