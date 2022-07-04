
import openpyxl
urls_category = ''
phone_availability = 0  # Число объявлений с телефонами
semafor = 30  # Количество потоков
links_item = []  # Список куда собираются все ссылки
parsed_link_count = 0  # Сколько ссылок обработано
find_links = 0  # Общее число найденных ссылок
directory = ''  # Папка для сохранения результата
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Юла"
row_title = [
    "Номер клиента",
    "Текст №1",
    "Имя клиента",
    "Текст №2",
    "Название товара",
    "Цена",
    "Текст №3"
]
# row_date =[
#     PhoneNum,
#     None,
#     owner_name,
#     None,
#     title_item,
#     price,
#     None
# ]


# row_title = [
#     "Id продавца",
#     "Имя продавца",
#     "Телефон",
#     "Местоположение",
#     "id товара",
#     "Название товара",
#     "Описание",
#     "Цена",
#     "Ссылка на товар",
#     "Фото"
# ]
# row_date =[
#     owner_id,
#     owner_name,
#     PhoneNum,
#     location,
#     id_item,
#     title_item,
#     description,
#     price,
#     link_item,
#     str(images_list)
# ]

# ws.append(row_title)


# wb.save('test.xlsx')

