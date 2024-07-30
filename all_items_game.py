import requests
import time
import json

APPID = 440
DEF_URL = "https://steamcommunity.com/market/search/render/"
PAGE_COUNT = 300

PAGE_SIZE = 100

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "sec-ch-ua-platform": "Windows"
}

def get_page(start):
    params = {
        "query" : "",
        "start" : str(start * PAGE_SIZE),
        "count" : str(PAGE_SIZE),
        "search_descriptions" : str(0),
        "sort_column" : "quantity",
        "sort_dir" : "desc",
        "appid" : str(APPID),
        "norender" : str(1)
    }
    res = requests.get(DEF_URL, params=params, headers=headers)
    if res.status_code != 200:
        return None
    if not res.json()["success"]:
        print(res.json())
        return None
    
    return res.json()['results']

if __name__ == "__main__":
    # page = get_page(0)
    # if (page != None):
    #     print(page[0])

    all_items = list()
    i = 0
    while (i < PAGE_COUNT):
        page = get_page(i)
        if page == None:
            time.sleep(90)
            continue

        items = list()
        for raw_item in page:
            item = {}
            item['hash_name'] = raw_item['hash_name']
            item['sell_listings'] = raw_item['sell_listings']
            item['sell_price'] = raw_item['sell_price']
            items.append(item)

        all_items.extend( items )

        with open(f'{APPID}.json', 'w') as file:
            json.dump(all_items, file)

        i += 1
        print(f'{i / PAGE_COUNT} %')
        time.sleep(15)
