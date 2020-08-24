import logging
import os
import time
import traceback
from datetime import datetime
from functools import wraps

import psycopg2
from bs4 import BeautifulSoup as bs
from config import Config
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s %(process)d:%(processName)s %(message)s',
                    filename='src/logs/service.log',
                    )
log = logging.getLogger(__name__)


# def quit_driver_and_reap_children(driver):
#     log.debug('Quitting session: %s' % driver.session_id)
#     driver.quit()
#     try:
#         pid = True
#         while pid:
#             pid = os.waitpid(-1, os.WNOHANG)
#             log.debug("Reaped child: %s" % str(pid))
#     except ChildProcessError:
#         pass


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
        log.info(f'function: {func.__name__} is worked {str(result_time)} sec')
        return result

    return timer


def audit(url, date1, date2, error, waste_time):
    with psycopg2.connect(dbname=Config.database_name,
                          user=Config.database_login,
                          password=Config.database_password,
                          host=Config.database_url,
                          port=Config.database_port) as conn, conn.cursor() as cur:
        cur.execute('''
        insert into adhoc_parser.audit_yandex_bot (url, report_date, parse_time, has_403, waste_time) values (%s, %s, %s, %s, %s)''',
                    (url, date1, date2, error, waste_time))


def get_page_keywords(html):
    soup = bs(html, 'lxml')
    try:
        keywords = soup.find('head').find_all('meta')
        title = soup.find('head').find('title')
        log.info(keywords)
        log.info(f'title from bs4: {str(title)}')
    except Exception as e:
        log.error(str(e) + traceback.format_exc())


def get_page_description(html):
    soup = bs(html, 'lxml')
    try:
        description = soup.find('head').find_all('meta', name_='description')
        log.info(description)
    except Exception as e:
        log.error(str(e) + traceback.format_exc())


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
        # self.chrome.implicitly_wait(20)
        self.default_url = 'https://yandex.ru/'
        self.search_words = search_words
        self.chrome = None
        # self.chrome.get(self.default_url)
        self.array = []

    @timer_logger
    def init(self):
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

    def quit_driver_and_reap_children(self):
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
    def take_promotion_urls(self):
        # self.array.append('https://fl-bankrotstvo.ru/')
        for x in self.array:
            log.debug(x)
        log.info(f'count with duplicates: {str(len(self.array))}')
        log.info(f'count without duplicates: {str(len(set(self.array)))}')
        return self.array

    @timer_logger
    def fetch_single_page(self, string):
        self.chrome.get(self.default_url)
        time.sleep(2.5)
        self.chrome.find_element_by_xpath('//*[@id="text"]').send_keys(f'{string}\n')
        html = self.chrome.page_source
        return html

    @timer_logger
    def get_data_from_html(self, raw_html):
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
            self.array.append('https://fl-bankrotstvo.ru/')
        except Exception as e:
            log.error(f'at this moment parser cant find url list from yandex page, pass with ERROR: {e}')

    @timer_logger
    def x(self):
        for i in self.search_words:
            self.get_data_from_html(self.fetch_single_page(i))


class TorDriver(DefaultDriver):

    def __init__(self, search_words: list):
        super().__init__(search_words)
        self.proxy = "socks5://127.0.0.1:9150"
        # self.options.add_argument(f'--proxy-server={self.proxy}')
        self.options.add_argument(f'user-agent={self.ua.random}')
        self.action = None

    def move_with_driver(self, item):
        try:
            self.action.move_to_element(item).perform()
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
            log.info(f'PAGE TITLE: {self.chrome.title}')
            get_page_keywords(self.chrome.page_source)
            # get_page_description(self.chrome.page_source)
            log.info(f'Current url parserd now: {self.chrome.current_url}')
            if 'yandex.ru/uslugi/' not in self.chrome.current_url and 'docs.google.com/forms/' not in self.chrome.current_url:
                if '403 Forbidden' not in self.chrome.page_source and '502 Bad Gateway' not in self.chrome.page_source:
                    has_error = 'N'
                    full_page = self.chrome.find_element_by_tag_name('html')
                    page_elements = self.chrome.find_elements_by_css_selector('div[class]')

                    scroll_page(full_page)
                    for element in page_elements[:10]:
                        self.move_with_driver(element)
                        # self.move_with_javascript(element, full_page)
                else:
                    log.error('403 Forbidden / 502 Bad Gateway')
                    has_error = 'Y'
                result_time = round(time.time() - start)

                audit(self.chrome.current_url, report_date, parse_time, has_error, result_time)
            else:
                log.warning('passed url with yandex.ru/uslugi/ or docs.google.com/forms/')
        except InvalidSessionIdException as e:
            has_error = 'F'
            # TODO try add self.init()
            # print((f'cant get page info, pass it with ERROR: {e}'))
            log.error(f'cant get page info, pass it with ERROR: {e}')
            audit('invalid session id', report_date, parse_time, has_error, 0)
