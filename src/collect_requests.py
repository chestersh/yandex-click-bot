from time import sleep

import psycopg2
import requests
from config import Config
from multiprocessing import Pool
from requests.exceptions import ConnectionError, ChunkedEncodingError

proxies = {
    'http': 'socks5://localhost:9150',
    'https': 'socks5://localhost:9150'
}

querry = 'select url from adhoc_parser.audit_yandex_bot'


from fake_useragent import UserAgent
ua = UserAgent()
print(ua.random)


with psycopg2.connect(dbname=Config.database_name, user=Config.database_login, password=Config.database_password,
                      host=Config.database_url,
                      port=Config.database_port) as conn, conn.cursor() as cur:
    cur.execute(querry)
    data = cur.fetchall()
    array = []
    for i in data:
        # print(i[0])
        array.append(i[0])
        # requests.get('http://httpbin.org/ip', proxies=proxies)
        # requests.get(i[0], proxies=proxies)
# while True:
#     data = requests.get('http://httpbin.org/ip', proxies=proxies)
#     print(data.text)
#     sleep(5)

# www = []
# for i in range(100):
#     www.append('http://77.244.65.15:3527/api/v1/data/promise/')

def get_request(url):
    headers = {'accept': '*/*',
               'user-agent': ua.random}
    try:
        data = requests.get(url, proxies=proxies, headers=headers)
        print(str(data.status_code), str(headers), url)
    except (ConnectionError, ChunkedEncodingError) as e:
        print(e)
        pass

with Pool(70) as pool:
    pool.map(get_request, array)



