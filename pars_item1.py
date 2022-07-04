import asyncio
import json
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
    while True:
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

        proxy_wrong_format = random.choice(proxy_list).split(':')
        proxies = f"http://{proxy_wrong_format[2]}:{proxy_wrong_format[3]}@{proxy_wrong_format[0]}:{proxy_wrong_format[1]}"
        try:
            async with session.get(url=link_item, headers=headers, proxy=proxies, ssl=False) as r:  #
                # print(f"{variables.link_total_count} сделал запрос")
                if r.status == 200:
                    html_cod = await r.text()
                    parrern = "(?<=window\.__YOULA_STATE__\ =\ ).*}"
                    YOULA_STATE = json.loads(re.search(parrern, html_cod).group())
                    if YOULA_STATE['entities']['products'][0]['owner']['store'] == None:  # проверка частник ли это
                        try:  # Есть ли поле с телефоном
                            PhoneNum = YOULA_STATE['entities']['products'][0]['owner']['displayPhoneNum']
                        except:
                            break  # Поля с телефоном нет
                        if PhoneNum != None:  # телефон есть
                            variables.phone_availability = variables.phone_availability + 1
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
                            path_json = Path(f"result {variables.directory}", f"{id_item}.xlsx")
                            with open(path_json, "w") as f:
                                json.dump(json_list, f)

                            # print(f"--------------\n{link_count} {link_item}\n{owner_id}\n{owner_name}\n{PhoneNum}\n{title_item}\n{description}\nцена {price}")
                            # print(f"--------------\n{link_count} {link_item}\nНайден номер {PhoneNum} {len(owner_id)}й\n---------------------")
                            # variables.owner_id.append(owner_id)
                            # variables.owner_id = temp


                            break
                        else:  # Телефона нет
                            # print(f"{link_count} {link_item}")
                            # print("нет телефона")
                            break
                    else:
                        # print("это не частник")
                        break  # это не частник, пропускаю
                elif r.status == 429:
                    count_proxy = count_proxy + 1
                    # print(f"код ошибки 429 меняю прокси {count_proxy}")  #  {count_proxy}
                    # pass
        except Exception as ex:  #
            if ex == 'Cannot connect to host youla.ru:443 ssl:False [None]':
                # print(f"ошибка 443 пауза {pause} сек")
                await asyncio.sleep(pause)
                pause = pause + 1
        except:
            print("не известная ошибка при запросе к странице товара")
    variables.parsed_link_count = variables.parsed_link_count + 1
    print(f"Обработано ссылок {variables.parsed_link_count} {link_item}", end='\r')
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
            task = asyncio.create_task(parser(session, semaphore, link_item))  # , variables.owner_id, link_count
            tasks.append(task)
        await asyncio.gather(*tasks)

def main():
    wb = variables.wb
    ws = variables.ws
    ws.title = 'Юла'
    ws.append(variables.row_title)
    asyncio.get_event_loop().run_until_complete(gahter())
    # today = datetime.datetime.today()
    # file_name = today.strftime("%Y-%m-%d_%H.%M.%S")
    path = Path(f"result {variables.directory}", "result.xlsx")
    wb.save(path)
    # wb.save(f'{file_name}.xlsx')


if __name__ == '__main__':
    main()
    # print(len(variables.owner_id))