import asyncio
import json, pr
import re
import aiohttp
from asyncio import Semaphore
from pathlib import Path
import variables
from user_agent import generate_user_agent
import random


async def parser(session, semaphore, link_item):  # , owner_id, link_count
    await semaphore.acquire()
    # print(f"передана ссылка {variables.link_total_count} {link_item}")
    json_list = []
    with open('proxies.txt', 'r') as f:
        proxy_text = f.read()
    proxy_list = proxy_text.split('\n')

    # await asyncio.sleep(2)

    pause = 2
    count_proxy = 0
    flag = True
    while flag == True:
        # print("запущен цикл")
        headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        try:
            async with session.get(url=link_item, headers=headers, ssl=False) as r:  #
                # print(f"статус код без прокси {r.status} Обработано ссылок {variables.parsed_link_count} {link_item}")
                if r.status == 200:
                    html_cod = await r.text()
                    ch = "без прокси"
                    flag = False
                elif r.status == 429:
                    proxy_wrong_format = random.choice(proxy_list).split(':')
                    proxies = f"http://{proxy_wrong_format[2]}:{proxy_wrong_format[3]}@{proxy_wrong_format[0]}:{proxy_wrong_format[1]}"
                    # print("пробую c прокси")
                    async with session.get(url=link_item, headers=headers, proxy=proxies, ssl=False) as r:  #
                        # print(f"статус код c прокси {r.status} Обработано ссылок {variables.parsed_link_count} {link_item}")
                        if r.status == 200:
                            html_cod = await r.text()
                            ch = "c прокси"
                            flag = False


                else:
                    pass
        except:
            pass
                # print(f"не получилось {ch} {r.status}")
        # print(f"облом {ch} пробую ещё раз")

    # print("вышел из цикла")
    parrern = "(?<=window\.__YOULA_STATE__\ =\ ).*}"
    YOULA_STATE = json.loads(re.search(parrern, html_cod).group())
    if YOULA_STATE['entities']['products'][0]['owner']['store'] == None:  # проверка частник ли это
        try:  # Есть ли поле с телефоном
            PhoneNum = YOULA_STATE['entities']['products'][0]['owner']['displayPhoneNum']
            if PhoneNum != None:  # телефон есть
                variables.phone_availability = variables.phone_availability + 1
                # print('\033[F!')
                print(f"Обработано ссылок {variables.parsed_link_count} {link_item} | Объявлений с телефонами {variables.phone_availability}")
                owner_id = YOULA_STATE['entities']['products'][0]['owner']['id']
                # temp = []
                # if owner_id not in variables.owner_id:
                owner_name = YOULA_STATE['entities']['products'][0]['owner']['name']
                title_item = YOULA_STATE['entities']['products'][0]['name']
                description = YOULA_STATE['entities']['products'][0]['description']
                location = YOULA_STATE['entities']['products'][0]['location']['description']
                id_item = YOULA_STATE['entities']['products'][0]['id']
                price_0 = YOULA_STATE['entities']['products'][0]['price']
                price = str(price_0)[:len(str(price_0)) - 2]

                images_list = []
                images = YOULA_STATE['entities']['products'][0]['images']
                for image in images:
                    images_list.append(image['url'])

                row_date =[
                    PhoneNum,
                    None,
                    owner_name,
                    None,
                    title_item,
                    price,
                    None
                ]
                variables.ws.append(row_date)

                json_list.append(
                    {
                        "photo": images_list,
                        "productname": title_item,
                        "price": price,
                        "adr": location,
                        "name": owner_name,
                        "cid": 564644223,
                        "owner": "random",
                        "id товара": id_item,
                        "Id продавца": owner_id,

                        # "Телефон": PhoneNum,
                        # "Описание": description,
                        # "Ссылка на товар": link_item,
                    }
                )
                path_json = Path(f"result {variables.directory}", f"{id_item}.json")
                with open(path_json, "w") as f:
                    json.dump(json_list, f)
            else:  # Телефона нет
                pass
        except:
            pass  # Поля с телефоном нет
    else:
        pass  # это не частник, пропускаю

    variables.parsed_link_count = variables.parsed_link_count + 1  # Обработано ссылок
    # print('\033[F!')
    print(f"Обработано ссылок {variables.parsed_link_count} | Объявлений с телефонами {variables.phone_availability} | {link_item}")
    semaphore.release()

async def gahter():
    semaphore = Semaphore(variables.semafor)
    tasks = []
    connector = aiohttp.TCPConnector(limit=20)
    # connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector) as session:  # ,  trust_env=True
        for link_count, link in enumerate(variables.links_item):  # [1:1000]
            # print("собираю tasks")
            link_item = f"https://youla.ru{link.strip()}"
            task = asyncio.create_task(parser(session, semaphore, link_item))
            tasks.append(task)
        await asyncio.gather(*tasks)


def main():

    wb = variables.wb
    ws = variables.ws
    ws.title = 'Юла'
    ws.append(variables.row_title)
    asyncio.get_event_loop().run_until_complete(gahter())
    path = Path(f"result {variables.directory}", "result.xlsx")
    wb.save(path)


if __name__ == '__main__':
    async def gahter():
        semaphore = Semaphore(variables.semafor)
        tasks = []
        with open('links_item.txt', 'r') as f:
            item = f.read()
        links_item = item.replace('[', '').replace(']', '').replace("'", '').split(',')
        connector = aiohttp.TCPConnector(limit=20)
        # connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=connector) as session:  # ,  trust_env=True
            for link_count, link in enumerate(links_item):  # [1:1000]
                # print("собираю tasks")
                link_item = f"https://youla.ru{link.strip()}"
                task = asyncio.create_task(parser(session, semaphore, link_item))  # , variables.owner_id, link_count
                tasks.append(task)
            await asyncio.gather(*tasks)
    main()
    # print(len(variables.owner_id))