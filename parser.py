import asyncio
import requests
from fake_useragent import FakeUserAgent
import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_DOWN


class ParserCentralBank:
    def __init__(self, loop):
        self.__url = "http://www.cbr.ru/scripts/XML_daily.asp"
        self.__fake = FakeUserAgent()
        self.__user_agent = {"user_agent": self.__fake.random}
        self.__response = requests.get(self.__url, params=self.__user_agent).text
        self.__root = ET.fromstring(self.__response)

        self.KGS = None
        self.USD = None
        self.TRY = None
        self.CNY = None

        loop.run_until_complete(self.fetch_exchange_rates())

    async def fetch_exchange_rates(self):
        self.KGS = await self.get_exchange_rate("Киргизских сомов")
        self.USD = await self.get_exchange_rate("Доллар США")
        self.TRY = await self.get_exchange_rate("Турецких лир")
        self.CNY = await self.get_exchange_rate("Китайский юань")

    async def get_exchange_rate(self, currency: str):
        ratio = [
            i.find("VunitRate").text
            for i in self.__root
            if i.find("Name").text == currency
        ][0]

        return str(ratio).replace(",", ".")

    async def currency_conversion(
        self,
        from_val: str = "RUB",
        to_val: str = "RUB",
        nominal: Decimal | float | int = 1,
    ):
        from_val, to_val = from_val.upper(), to_val.upper()

        # Убеждаемся, что nominal преобразован в Decimal
        nominal = Decimal(str(nominal))

        # Предположим, что dicts уже заполнен и содержит строки, которые можно преобразовать в Decimal
        dicts = {
            "USD": Decimal(self.USD),
            "KGS": Decimal(self.KGS),
            "CNY": Decimal(self.CNY),
            "TRY": Decimal(self.TRY),
        }

        if from_val == to_val:
            return nominal
        else:
            if from_val == "RUB":
                result = nominal / dicts[to_val]
            elif to_val == "RUB":
                result = nominal * dicts[from_val]
            else:
                result = (nominal * dicts[from_val]) / dicts[to_val]

            # Округление результата до трех знаков после запятой
            return result.quantize(Decimal("1.000"), ROUND_HALF_DOWN)


loop = asyncio.get_event_loop()
pars = ParserCentralBank(loop)
