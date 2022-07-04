import asyncio
from asyncio import Semaphore

import re

import variables
from variables import semafor, links_item
import aiohttp
from user_agent import generate_user_agent
import time
import json

async def parser_links_from_category(session, semaphore, url):  #
    await semaphore.acquire()
    url_api = "https://api-gw.youla.io/federation/graphql"
    page = 0
    totalProductsCount = 0
    hasNextPage = True

    id_category = url.split('?')[0].split('/')[-1]
    slug_categories = {  # обязательный словарь, прилепить в конце списка attributes
        'slug': 'categories',
        'value': [f'{id_category}'],
        'from': None,
        'to': None,
    }

    attributes = []
    datePublished = None
    if str(url).find('?attributes') != -1:  # Если есть фильтры
        attributes_list = str(url).split('?')[1].split('&')
        value = []
        slug_0 = ''
        from_ = ''
        to = ''
        name_for_dict = []
        datePublished_flag = True
        for i, attr in enumerate(attributes_list):
            slug = re.findall('(?<=\[).*?(?=])', attr)[0]
            if slug == "term_of_placement":
                if datePublished_flag == True:
                    datePublished = {}
                    datePublished["to"] = int(str(time.time()).split('.')[0])# время сейчас
                    val_from = attr.split('=')[-1].split('%')[0].replace("-", "")
                    from_ = int(datePublished["to"]) - int(val_from) * 86400
                    datePublished["from"] = from_  # время - 7 или 1 дней
                    datePublished_flag = False
                else:
                    pass
            else:
                try:
                    if attributes[-1]['slug'] == slug:
                        pass
                    else:
                        value = []
                        attributes.append(slug)
                        attributes[-1] = {}
                except:
                    value = []
                    attributes.append(slug)
                    attributes[-1] = {}

                val = attr.split('=')[-1]
                if str(re.findall('(?<=\[).*?(?=])', attr)[1]).find('from') != -1:
                    from_ = int(val)
                elif str(re.findall('(?<=\[).*?(?=])', attr)[1]).find('to') != -1:
                    to = int(val)
                else:
                    from_ = None
                    to = None
                    value.append(val)
                attributes[-1]["slug"] = slug
                attributes[-1]["value"] = value
                attributes[-1]["from"] = from_
                attributes[-1]["to"] = to
        attributes.append(slug_categories)
        # print("собрал attributes")

    else:  # Если в ссылке нет фильтров
        attributes.append(slug_categories)





    while hasNextPage == True:
        headers = {
            'User-Agent': generate_user_agent(),
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'content-type': 'application/json',
            'x-app-id': 'web/3',
            'x-uid': '62b75523719d5',
            'x-youla-splits': '8a=8|8b=8|8c=0|8m=0|8v=0|8z=0|16a=0|16b=0|64a=3|64b=0|100a=12|100b=4|100c=0|100d=0|100m=0',
            'appId': 'web/3',
            'uid': '62b75523719d5',
            'Origin': 'https://youla.ru',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://youla.ru/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        json_data = {
            'operationName': 'catalogProductsBoard',
            'variables': {
                'sort': 'DEFAULT',
                'attributes': attributes,
                'datePublished': datePublished,
                'location': {
                    'latitude': None,
                    'longitude': None,
                    'city': 'all',
                    'distanceMax': None,
                },
                'search': '',
                # 'cursor': '',
                # 'cursor': '{\"page\":23,\"totalProductsCount\":30,\"totalPremiumProductsCount\":2,\"dateUpdatedTo\":1656233988}',
                'cursor': '{\"page\":' + str(page) + ',\"totalProductsCount\":' + str(totalProductsCount) + ',\"totalPremiumProductsCount\":2,\"dateUpdatedTo\":' + str(time.time()).split('.')[0] + '}',
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '6e7275a709ca5eb1df17abfb9d5d68212ad910dd711d55446ed6fa59557e2602',
                },
            },
        }
        async with session.post(url=url_api, headers=headers, json=json_data) as r:
            # print(url_category)
            html_cod = await r.text()
            json_data = json.loads(html_cod)
            item_urls = json_data['data']['feed']['items']  # [1]['product']['url']
            for url in item_urls:
                if url['__typename'] == 'AdvertItem':  # or 'LocationLabelPlacementItem':
                    pass
                elif url['__typename'] == 'LocationLabelPlacementItem':
                    pass
                # elif url['product']['url'] == 'None':
                #     pass
                else:
                    url_item = url['product']['url']
                    if url_item not in links_item:  # борьба с дублями
                        if url_item != None:
                            # print(f"{id_category} {url_item}")
                            links_item.append(url_item)
                            variables.find_links = variables.find_links + 1  # Найдено ссылок
                            print(f"Найдено ссылок {variables.find_links}")
                        else: pass
                    #
            hasNextPage = json_data['data']['feed']['pageInfo']['hasNextPage']
            page += 1
            totalProductsCount = totalProductsCount + 30
    # print(len(links_item))

    semaphore.release()


async def gahter_links_items():

    semaphore = Semaphore(30)
    with open('links_category.txt', 'r') as f:
        urls_category_list = f.read().split('\n')
    # urls_category_list = variables.urls_category.split('\n')  # для работы с ссылками из textarea
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls_category_list:
            task = asyncio.create_task(parser_links_from_category(session, semaphore, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

def main():
    asyncio.get_event_loop().run_until_complete(gahter_links_items())

if __name__ == '__main__':
    main()
    # print("записал в файл")
    with open('links_item.txt', 'w') as f:
        f.write(str(links_item))

