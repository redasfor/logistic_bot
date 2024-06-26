# Калькулятор логистики

### Краткое описание 
Данный проект реализован в виде бесплатного бота в telegram. Каждому новому пользователю предоставляется возможность заполнить шаблон, последовательно ответив на вопросы о товаре, и затем сохранить его.
После чего за пользователем закрепляется его шаблон и он может просматривать все свои заполненные шаблоны, а также добавлять новые.
Предоставляется удобное меню в формате inline кнопок и всего одна команда /start

### Основные задачи бота
* Снижение финансовых издержек на логистику товара из нескольких стран-экспортёров путем мониторинга официального курса валют;
* Самостоятельный расчет - Вы вводите данные в одном виде, а дальше бот считает их за Вас и самостоятельно конвертирует из одной валюты в другую при необходимости;
* Хранение всех заполненных шаблонов в одном месте

## Использованный стек
1. Язык программирования: **Python**
2. Асинхронные библиотеки: **asyncio**
3. Telegram bot: **aiogram**
4. Парсинг: **requests, fake_useragent, xml.etree.ElementTree**
5. БД: **PostgreSQL, SQLAlchemy.orm, Alembic**
6. Кэширование: **Redis**
7. Валидация данных: **pydantic**
8. Логирование: **logging**
9. Деплой: **Git, Docker**
10. Паттерны: **DAO**

## Парсер
Получает актуальную информацию о курсах валют на сегодня с официального сайта [ЦБРФ](https://www.cbr.ru/ "нажмите для перехода на сайт ЦБРФ")

**Доступные валюты:**
* Российский рубль (RUB)
* Американский доллар (USD)
* Китайский юань (CNY)
* Турецкая лира (TRY)
* Киргизский сом (KGS)

Когда Вы открываете на просмотр любой из сохраненных шаблонов, Вы можете не беспокоиться о корректности полученной итоговой стоимости логистики,
все значения снова прогонятся через парсер и цифры обновятся с учетом нового курса валют

## Перспектива развития
Доработка и подключение бота под различные логистические компании для удобного взаимодействия со своей аудиторией и поиска/привлечения новой потенциальной аудитории
