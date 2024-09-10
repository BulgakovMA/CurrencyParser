import requests
import uvicorn
from typing import List
from fastapi import FastAPI
from bs4 import BeautifulSoup
from pydantic import BaseModel


app = FastAPI()


class CurrencyInput(BaseModel):
    quantity: float


class CurrencyRate(BaseModel):
    id_code: str
    letter_code: str
    units: str
    currency: str
    exchange_rate: float
    quantity: float
    amount: float


def get_currency_rates(html, quantity: float) -> List[CurrencyRate]:
    result = []
    soup = BeautifulSoup(html.text, features="lxml")
    line = soup.find(class_="table-wrapper").find_all("tr")

    for row in line:
        cells = row.find_all('td')
        if cells and cells[1].text == 'USD':
            id_code = cells[0].text
            letter_code = cells[1].text
            units = cells[2].text
            currency = cells[3].text
            exchange_rate = float(cells[4].text.strip().replace(',', '.'))
            amount = quantity * exchange_rate

            result.append(CurrencyRate(id_code=id_code, letter_code=letter_code,
                  units=units, currency=currency, exchange_rate=exchange_rate,
                  quantity=quantity, amount=amount))
    return result

@app.post("/currency/")
async def user_input(currency_input: CurrencyInput) -> List[CurrencyRate]:
    url = "https://cbr.ru/currency_base/daily//"
    quantity = currency_input.quantity
    response = requests.get(url)
    rates = get_currency_rates(response, quantity)
    return rates


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)