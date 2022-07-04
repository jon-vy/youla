import datetime
import os
import links_items
import pars_item
import variables
from pathlib import Path
today = datetime.datetime.today()
variables.directory = today.strftime("%Y-%m-%d_%H.%M.%S")
path = Path("result", f"result {variables.directory}")
os.mkdir(path)

links_items.main()
pars_item.main()
print("работа закончена. Для выхода нажми enter")
input()

