import logging
import os
import time
import traceback
from datetime import datetime
from functools import wraps

import psycopg2
import requests
from bs4 import BeautifulSoup as bs
from config import Config
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s - %(message)s',
                    filename='src/logs/service.log',
                    # filename='logs/service.log',
                    )
log = logging.getLogger(__name__)


def scroll_page(html):
    html.send_keys(Keys.ESCAPE)
    for i in range(100):
        html.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.05)
    for i in range(6):
        html.send_keys(Keys.PAGE_UP)
        time.sleep(0.1)


def timer_logger(func):
    @wraps(func)
    def timer(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        result_time = time.time() - start
        log.info(f'function: {func.__name__} is worked {str(round(result_time, 2))} sec')
        return result

    return timer


def audit(url, report_date, parse_time, has_error, waste_time, title, ip, meta):
    with psycopg2.connect(dbname=Config.database_name,
                          user=Config.database_login,
                          password=Config.database_password,
                          host=Config.database_url,
                          port=Config.database_port) as conn, conn.cursor() as cur:
        cur.execute('''
        insert into adhoc_parser.audit_yandex_bot (url, report_date, parse_time, has_403, waste_time, title, ip, meta) values (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (url, report_date, parse_time, has_error, waste_time, title, ip, meta))


def get_meta_data(html: str):
    soup = bs(html, 'lxml')
    try:
        meta = soup.find('head').find_all('meta')
        log.info(meta)
        return meta
    except Exception as e:
        log.error(str(e) + traceback.format_exc())
        return None


class DefaultDriver:

    def __init__(self, search_words: list):
        self.ua = UserAgent()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-agent={self.ua.random}')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--window-size=1420,1080')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.default_url = 'https://yandex.ru/'
        self.search_words = search_words
        self.chrome = None
        self.array = []

    @staticmethod
    def get_my_public_id() -> str:
        data = requests.get('http://icanhazip.com')
        ip = data.text.strip()
        return ip

    @timer_logger
    def init(self) -> None:
        self.chrome = webdriver.Chrome(options=self.options)
        self.chrome.implicitly_wait(120)
        time.sleep(2)

    def close(self) -> None:
        try:
            self.chrome.close()
            self.chrome.quit()
        except InvalidSessionIdException as e:
            log.error(f'Error with close driver : {e}')
        except WebDriverException as e:
            log.error(f'Error with close driver : {e}')

    def quit_driver_and_reap_children(self) -> None:
        log.warning('Quitting session: %s' % self.chrome.session_id)
        self.chrome.quit()
        try:
            pid = True
            while pid:
                pid = os.waitpid(-1, os.WNOHANG)
                log.warning("Reaped child: %s" % str(pid))
        except ChildProcessError:
            pass

    @timer_logger
    def take_promotion_urls(self) -> list:
        for x in self.array:
            log.debug(x)
        log.info(f'count with duplicates: {str(len(self.array))}')
        log.info(f'count without duplicates: {str(len(set(self.array)))}')
        return self.array

    @timer_logger
    def fetch_single_page(self, string) -> str:
        self.chrome.get(self.default_url)
        time.sleep(2.5)
        self.chrome.find_element_by_xpath('//*[@id="text"]').send_keys(f'{string}\n')
        time.sleep(1.5)
        html = self.chrome.page_source
        return html

    @timer_logger
    def get_data_from_html(self, raw_html) -> None:
        soup = bs(raw_html, 'lxml')
        try:
            search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
            array = []
            for element in search_array:
                if element.get('data-cid') is not None:
                    if element.find('div', class_='organic__url-text') is not None:
                        if 'fl-bankrotstvo.ru' not in element.find('div').text:
                            if 'prodolgi40.ru' not in element.find('div').text:
                                array.append(element)
            for array_element in array:
                if 'yabs.yandex.ru' in array_element.find('div').find('a').get('href'):
                    url = array_element.find('div').find('a').get('href')
                    self.array.append(url)
            # self.array.append('https://fl-bankrotstvo.ru/')
            # self.array.append('https://quiz.fl-bankrotstvo.ru/')
        except Exception as e:
            log.error(
                f'at this moment parser cant find url list from yandex page, pass with ERROR: {str(e) + traceback.format_exc()}')

    @timer_logger
    def x(self):
        for i in self.search_words:
            self.get_data_from_html(self.fetch_single_page(i))


class TorDriver(DefaultDriver):

    def __init__(self, search_words: list):
        super().__init__(search_words)
        self.proxy = "socks5://localhost:9050"
        # self.options.add_argument(f'--proxy-server={self.proxy}')
        self.options.add_argument(f'user-agent={self.ua.random}')
        self.action = None

    def move_with_driver(self, item) -> None:
        try:
            self.action.move_to_element(item).perform()
            time.sleep(0.1)
        except Exception as e:
            pass

    def move_with_javascript(self, item, html) -> None:
        try:
            self.chrome.execute_script(f'"arguments[0].scrollIntoView();", {item}')
            self.action.move_to_element(item).perform()
            html.send_keys(Keys.ESCAPE)
            time.sleep(0.2)
        except Exception as e:
            pass

    @timer_logger
    def start(self, url) -> None:
        ip = self.get_my_public_id()
        report_date = datetime.today().strftime('%Y-%m-%d')
        parse_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        start = time.time()
        self.action = ActionChains(self.chrome)
        try:
            self.chrome.get(url)
            title = self.chrome.title
            log.info(f'Title from this page: {title}')
            meta = str(get_meta_data(self.chrome.page_source))
            log.info(f'Current url parserd now: {self.chrome.current_url}')
            if 'yandex.ru/uslugi/' not in self.chrome.current_url and 'docs.google.com/forms/' not in self.chrome.current_url:
                if '403 Forbidden' not in self.chrome.page_source and '502 Bad Gateway' not in self.chrome.page_source:
                    has_error = 'N'
                    full_page = self.chrome.find_element_by_tag_name('html')
                    page_elements = self.chrome.find_elements_by_css_selector('div[class]')

                    scroll_page(full_page)
                    for element in page_elements[:10]:
                        self.move_with_driver(element)
                else:
                    log.error('403 Forbidden / 502 Bad Gateway')
                    has_error = 'Y'
                result_time = round(time.time() - start)

                audit(self.chrome.current_url, report_date, parse_time, has_error, result_time, title, ip, meta)
            else:
                log.warning('passed url with yandex.ru/uslugi/ or docs.google.com/forms/')
        except InvalidSessionIdException as e:
            log.error(f'cant get page info, pass it with ERROR: {str(e) + traceback.format_exc()}')
            audit('invalid session id', report_date, parse_time, 'F', 0, None, ip, None)
