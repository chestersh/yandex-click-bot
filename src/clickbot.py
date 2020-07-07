from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from functools import wraps
from config import Config
from proxy_agents import user_agent_catalina
from typing import Union, List
import requests
from bs4 import BeautifulSoup as bs
import random
import logging
import time
import psycopg2
from datetime import datetime
from selenium.common.exceptions import InvalidSessionIdException

def test1(command:str, params:tuple) -> str:
    pass
def test2(command:str, params:tuple) -> None:
    pass
def hundreds(x: Union[int, float]) -> int:
    pass


def timer_logger(func):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(funcName)s %(process)d:%(processName)s [%(levelname)s] %(message)s', filename='./vol_logs/clickbot.log')
    log = logging.getLogger(__name__)

    @wraps(func)
    def timer(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        result_time = time.time() - start
        log.info(f'function: {func.__name__} is worked {str(result_time)} sec')
        return result

    return timer


class DefaultDriver:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(funcName)s %(process)d:%(processName)s [%(levelname)s] %(message)s', filename='./vol_logs/clickbot.log')
    log = logging.getLogger(__name__)

    def __init__(self, search_words: list):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-agent={user_agent_catalina}')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        # self.chrome = webdriver.Chrome(options=self.options)
        # self.chrome.implicitly_wait(20)
        self.default_url = 'https://yandex.ru/'
        self.search_words = search_words
        self.chrome = None
        # self.chrome.get(self.default_url)
        self.array = []

    def audit(self, url, date1, date2, error, waste_time):
        with psycopg2.connect(dbname=Config.database_name, user=Config.database_login, password=Config.database_password, host=Config.database_url,
                              port=Config.database_port) as conn, conn.cursor() as cur:
            cur.execute('''
            insert into adhoc_parser.audit_yandex_bot (url, report_date, parse_time, has_403, waste_time) values (%s, %s, %s, %s, %s)''', (url, date1, date2, error, waste_time))
        print('INSERT')


    @timer_logger
    def init(self):
        self.chrome = webdriver.Chrome(options=self.options)
        self.chrome.implicitly_wait(200)
        time.sleep(2)

    def close(self) -> None:
        try:
            self.chrome.close()
        except InvalidSessionIdException:
            pass

    @timer_logger
    def take_promotion_urls(self):
        for x in self.array:
            self.log.warning(x)
        self.log.info(f'count with duplicates: {str(len(self.array))}')
        self.log.info(f'count without duplicates: {str(len(set(self.array)))}')
        return self.array

    @timer_logger
    def fetch_single_page(self, string):
        self.chrome.get(self.default_url)
        time.sleep(2.5)
        self.chrome.find_element_by_xpath('//*[@id="text"]').send_keys(f'{string}\n')
        html = self.chrome.page_source
        print('FETCH SINGLE PAGE')
        return html

    @timer_logger
    def get_data_from_html(self, raw_html):
        soup = bs(raw_html, 'lxml')
        try:
            search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
            array = [j for j in search_array if j.get('data-cid') is not None and j.find('div', class_='organic__url-text') is not None and 'fl-bankrotstvo.ru' not in j.find('div').text and 'prodolgi40.ru' not in j.find('div').text]
            [self.array.append(url.find('div').find('a').get('href')) for url in array if 'yabs.yandex.ru' in url.find('div').find('a').get('href')]
        except Exception as e:
            self.log.error(f'at this moment parser cant find url list from yandex page, pass with ERROR: {e}')

    @timer_logger
    def x(self):
        for i in self.search_words:
            self.get_data_from_html(self.fetch_single_page(i))

# #search-result > li:nth-child(3) > div > div.organic__subtitle.organic__subtitle_nowrap.typo.typo_type_greenurl > div.path.path_show-https.organic__path > a > b
# //*[@id="search-result"]/li[1]/div/div[1]/div[1]/a/b
kw_temp = [
    'банкротство юридических лиц',
    'банкротство юридических лиц калужская область',
    'банкротство юридических лиц обнинск',
    'банкротство юридических лиц Боровск',
    'банкротство юридических лиц Наро-Фоминск',
    'банкротство юридических лиц Малоярославец',

    'банкротство граждан',
    'банкротство граждан обнинск',
    'банкротство граждан Наро-Фоминск',
    'банкротство граждан Боровск',
    'банкротство граждан калужская область',
    'банкротство граждан Малоярославец',
    'банкротство граждан Балабаново',
    'банкротство граждан Ермолино',

    'Законное списание долгов',
    'Законное списание долгов Обнинск',
    'Законное списание долгов Наро-Фоминск',
    'Законное списание долгов Боровск',
    'Законное списание долгов Ермолино',
    'Законное списание долгов калужская область',
    'Законное списание долгов Малоярославец',
    'Законное списание долгов Балабаново',

    'Списать долги',
    'Списать долги Обнинск',
    'Списать долги Ермолино',
    'Списать долги Боровск',
    'Списать долги Наро-Фоминск',
    'Списать долги Балабаново',
    'Списать долги Малоярославец',
    'Списать долги калужская облсть',

    'Как списать долги',
    'Как списать долги обнинск',
    'Как списать долги Наро-Фоминск',
    'Как списать долги Боровск',
    'Как списать долги Балабаново',
    'Как списать долги Ермолино',
    'Как списать долги Малоярославец',
    'Как списать долги калужская область',

    'Банкротство физических лиц минусы',
    'Справка по банкротству физических лиц',

]

kw = [
    'банкротство юридических лиц обнинск',
    'банкротство граждан',
]


class TorDriver(DefaultDriver):

    def __init__(self, search_words: list):
        super().__init__(search_words)
        self.proxy = "socks5://127.0.0.1:9150"
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=820,640')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        # self.options.add_argument(f'--proxy-server={self.proxy}')
        self.options.add_argument(f'user-agent={user_agent_catalina}')
        self.action = None

    def move_with_driver(self, item, html):
        try:
            self.action.move_to_element(item).perform()
            html.send_keys(Keys.ESCAPE)
            html.send_keys(Keys.PAGE_DOWN)
            for i in range(5):
                html.send_keys(Keys.ARROW_UP)
            html.send_keys(Keys.PAGE_DOWN)
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)
        except Exception as e:
            pass

    def move_with_javascript(self, item, html):
        try:
            self.chrome.execute_script(f'"arguments[0].scrollIntoView();", {item}')
            self.action.move_to_element(item).perform()
            html.send_keys(Keys.ESCAPE)
            time.sleep(0.2)
        except Exception as e:
            pass

    @timer_logger
    def start(self, url):
        report_date = datetime.today().strftime('%Y-%m-%d')
        parse_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        start = time.time()
        self.action = ActionChains(self.chrome)
        try:
            self.chrome.get(url)
            self.log.info(f'Current url parserd now: {self.chrome.current_url}')
            if 'yandex.ru/uslugi/' not in self.chrome.current_url and 'docs.google.com/forms/' not in self.chrome.current_url:
                if '403 Forbidden' not in self.chrome.page_source and '502 Bad Gateway' not in self.chrome.page_source:
                    has_error = 'N'
                    full_page = self.chrome.find_element_by_tag_name('html')
                    page_elements = self.chrome.find_elements_by_css_selector('div[class]')

                    for element in page_elements[:8]:
                        self.move_with_driver(element, full_page)
                        # self.move_with_javascript(element, full_page)
                else:
                    self.log.error('403 Forbidden / 502 Bad Gateway')
                    has_error = 'Y'
                result_time = round(time.time() - start)

                self.audit(self.chrome.current_url, report_date, parse_time, has_error, 100)
            self.log.warning('passed url with yandex.ru/uslugi/ or docs.google.com/forms/')
        except Exception as e:
            self.log.error(f'cant get page info, pass it with ERROR: {e}')

#
# while True:
#     prepare = DefaultDriver(kw)
#     prepare.init()
#     prepare.x()
#     data = prepare.take_promotion_urls()
#     prepare.close()
#
#     tor = TorDriver(kw)
#     tor.init()
#     for url in data:
#         tor.start(url)
#     tor.close()
#     time.sleep(300)