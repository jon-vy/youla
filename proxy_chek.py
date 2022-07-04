import requests
from bs4 import BeautifulSoup
import lxml

with open('proxies.txt', 'r') as f:
    proxy_text = f.read()
proxy_list = proxy_text.split('\n')

for pr in proxy_list:
    p = pr.split(':')
    prox = f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
# proxies = {'https': f'http://{login}:{password}@{ip}:{port}'}
    proxies = {'https': prox}

    url = "https://2ip.ru/"
    r = requests.get(url=url, proxies=proxies)
    html_cod = r.text
    soup = BeautifulSoup(html_cod, 'lxml')
    ip = soup.find('div', id='d_clip_button').text.strip()
    print(ip)