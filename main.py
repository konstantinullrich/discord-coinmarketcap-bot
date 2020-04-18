import time
from datetime import datetime
import requests
import json

delay = 1800  # seconds
discord_webhook = 'MY_WEBHOOK'  # enter in your webhook url
currencies_list = [1, 1027, 2, 2748, 328, 74]
fiat = 'USD'

'''
Symbol - CoinMarketCap ID
BTC - 1
ETH - 1027
LTC - 2
LOKI - 2748
XMR - 328
DOGE - 74
'''

'''
donate me a cup of coffee using:
ETH: 0xCf99569890771d869BfC28C776D07F59b0636D72
'''


class Cryptocurrency:
    def __init__(self, name: str, symbol: str):
        self.name = name
        self.symbol = symbol
        self.price = 0

    def set_price(self, price: float): self.price = price

    @property
    def get_name(self): return self.name

    @property
    def get_symbol(self): return self.symbol

    @property
    def get_price(self): return self.price

    @property
    def get_title(self):
        if len(self.symbol) == 0:
            return self.get_name
        return '{} ({})'.format(self.get_name, self.get_symbol)


def get_cryptocurrency(coinmarketcap_id: int):
    price_url = 'https://widgets.coinmarketcap.com/v2/ticker/{}?convert={}'.format(coinmarketcap_id, fiat)
    request = requests.get(price_url)
    if request.status_code == 200:
        request = json.loads(request.text)
        request = request['data']
        currency = Cryptocurrency(request['name'], request['symbol'])
        try:
            currency.set_price(request['quotes'][fiat]['price'])
        except KeyError:
            currency.set_price(request['quotes']['USD']['price'])
        return currency
    print('Failed to fetch quotes.\nPossible error:\n\t- Invalid CoinmarketcapId')
    return False


def push_to_discord(currencies: list) -> str:
    fields = []
    for currency in currencies:
        price = get_cryptocurrency(currency)
        if price:
            fields.append({
                'name': price.get_title,
                'value': '$ ' + str(price.get_price),
                'inline': True
            })
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
    embeds = [{
        'type': 'rich',
        'color': 123456,
        'timestamp': timestamp,
        'fields': fields
    }]
    payload = {'embeds': embeds}
    r = requests.post(discord_webhook, json=payload)
    if r.status_code != 204:
        print('Failed to push Webhook.\nPossible error:\n\t- Invalid Webhook')
    return timestamp


if __name__ == '__main__':
    while True:
        pushed_timestamp = push_to_discord(currencies_list)
        print(pushed_timestamp)  # print to console to make sure program isn't frozen
        time.sleep(delay)
