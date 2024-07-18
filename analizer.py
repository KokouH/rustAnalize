import requests
import json
import time
import datetime
import numpy as np
from loguru import logger

appid = 252490
url = f'https://steamcommunity.com/market/listings/{appid}/'

# Calcualte BLOCK
get_x = lambda history, as_int=False: [i[0] if not as_int else i[0].timestamp() - history[0][0].timestamp() for i in history]
get_y = lambda history: [i[1] for i in history]
get_last_month = lambda history: [i for i in history[::-1] if (history[-1][0] - i[0]).total_seconds() < 86400 * 30 ][::-1]
get_low_price = lambda history, percent=0.1: sorted(history, key=lambda m: m[1])[int(len(history) * percent)]
get_high_price = lambda history, percent=0.9: sorted(history, key=lambda m: m[1])[int(len(history) * percent)]

_get_z = lambda history: np.polyfit(np.array(get_x(history, True),), np.array(get_y(history), dtype=float), 1)
_get_p = lambda history: np.poly1d(_get_z(history))
get_trend = lambda history: _get_p(history)(get_x(history, True)[-1]) / _get_p(history)(0)

# Steam calls BLOCK
#accessory funcs
_get_start = lambda text: text.find('var line1=')
_get_raw_history = lambda text: json.loads(text[_get_start(text) + 10 : _get_start(text) + text[_get_start(text):].find(']]') + 2])
_get_date = lambda date_text: datetime.datetime.strptime(date_text, '%b %d %Y %H')

#main funcs
get_page = lambda hash_name: requests.get(url + hash_name).text
get_history = lambda text: [[_get_date(i[0][:14]), i[1], int(i[2])] for i in _get_raw_history(text)]
get_sell_per_days = lambda history, dayCount: sum( [i[2] for i in history if (datetime.datetime.now() - i[0]).total_seconds() < 86400 * dayCount] )

if __name__ == "__main__":
    logger.add("file_{time}.log", level="TRACE", rotation="100 MB")

    with open('rust.json', 'r') as file:
        items = json.load(file)

    hash_names = [i['hash_name'] for i in items]

    out_file = open('good.json', 'w')
    hashSize = len(hash_names) - 1
    for cur_ind, hash_name in enumerate(hash_names):
        try:
            item = dict()
            page = get_page(hash_name)
            history = get_last_month( get_history(page) ) # only last month

            low = get_low_price(history)
            high = get_high_price(history)
            trend = get_trend(history)

            item['hash_name'] = hash_name
            item['trend'] = trend
            item['low'] = low[1]
            item['high'] = high[1]
            item['month_sells'] = sum( i[2] for i in history )

            out_file.write( json.dump(item) )
            out_file.flush()

        except Exception as e:
            logger.error(f"{hash_name}")
            time.sleep(60)
        finally:
            logger.info(f"{int(cur_ind / hashSize * 100)} % | {hash_name}")
            time.sleep(5)

    out_file.close()

