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


def test1(command:str, params:tuple) -> str:
    pass
def test2(command:str, params:tuple) -> None:
    pass
def hundreds(x: Union[int, float]) -> int:
    pass


def timer_logger(func):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(funcName)s %(process)d:%(processName)s [%(levelname)s] %(message)s', filename='clickbot.log')
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

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(funcName)s %(process)d:%(processName)s [%(levelname)s] %(message)s', filename='clickbot.log')
    log = logging.getLogger(__name__)

    def __init__(self, search_words: list):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(f'user-agent={user_agent_catalina}')
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
            insert into adhoc_parser.audit_test (url, report_date, parse_time, has_403, waste_time) values (%s, %s, %s, %s, %s)''', (url, date1, date2, error, waste_time))


    @timer_logger
    def init(self):
        self.chrome = webdriver.Chrome(options=self.options)
        self.chrome.implicitly_wait(1000)
        time.sleep(2)

    def close(self) -> None:
        self.chrome.close()

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
        self.chrome.find_element_by_xpath('//*[@id="text"]').send_keys(f'{string}\n')
        html = self.chrome.page_source
        return html

    @timer_logger
    def get_data_from_html(self, raw_html):
        soup = bs(raw_html, 'lxml')
        search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
        array = [j for j in search_array if j.get('data-cid') is not None and j.find('div', class_='organic__url-text') is not None and 'fl-bankrotstvo.ru' not in j.find('div', class_='organic__url-text').text and 'prodolgi40.ru' not in j.find('div', class_='organic__url-text').text]
        [self.array.append(url.find('div').find('a').get('href')) for url in array if 'yabs.yandex.ru' in url.find('div').find('a').get('href')]

    @timer_logger
    def x(self):
        for i in self.search_words:
            self.get_data_from_html(self.fetch_single_page(i))


kw = ['банкротство юридических лиц обнинск', 'банкротство граждан']


class TorDriver(DefaultDriver):

    def __init__(self, search_words: list):
        super().__init__(search_words)
        self.proxy = "socks5://127.0.0.1:9150"
        self.options.add_argument(f'--proxy-server={self.proxy}')
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
            time.sleep(0.3)
        except Exception as e:
            pass

    def move_with_javascript(self, item, html):
        try:
            self.chrome.execute_script('"arguments[0].scrollIntoView();", j')
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
        self.chrome.get(url)
        self.log.info(f'Current url parserd now: {self.chrome.current_url}')
        if '403 Forbidden' not in self.chrome.page_source:
            has_error = 'N'
            full_page = self.chrome.find_element_by_tag_name('html')
            page_elements = self.chrome.find_elements_by_css_selector('div[class]')

            for element in page_elements[:3]:
                self.move_with_driver(element, full_page)
                # self.move_with_javascript(element, full_page)
        else:
            self.log.error('403 Forbidden')
            has_error = 'Y'
        result_time = round(time.time() - start)

        self.audit(self.chrome.current_url, report_date, parse_time, has_error, result_time)


prepare = DefaultDriver(kw)
prepare.init()
prepare.x()
data = prepare.take_promotion_urls()
prepare.close()


tor = TorDriver(kw)
tor.init()
for url in data:
    tor.start(url)
tor.close()



















#
#
# def test_parse():
#     with open('training.html', 'r') as file:
#         data = file.read()
#     soup = bs(data, 'lxml')
#     search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
#     array = [j for j in search_array if j.get('data-cid') is not None and j.find('div', class_='organic__url-text') is not None and 'fl-bankrotstvo.ru' not in j.find('div', class_='organic__url-text').text]
#     # print(len(search_array))
#     print(len(array))
#     for i in array:
#         print(i)
#         print(i.find('div', class_='organic__url-text').text)
#         print(i.find('div').find('a').get('href'))
#         print('--------')

# test.x()
# test.take_promotion_urls()
# test_parse()


#1 http://yabs.yandex.ru/count/WaKejI_zOES1tH40P1v8kfVX0N6iPGK0vm8GWX0nsf3uNW00000u109mmkYfaWY00QM8ZtI80P_5ZVLEa076mjJcn820W0AO0SR2rEP4k07amgx17y01NDW1qg_e7-01-8wU7-W1W06W0gQqtnNO0WBm0eopxz86c0FAdY2W0mRGXWFu1DNkVuW5rUv_a0NmrUq1e0MSWIUe1OB18B05Wi4Wk0MmjZp01V3LxG781R2sFAAsiUW5e0QE3wW6ZW_91jIu0L0ceFSpqGRKJ3V79g3tC-TTv2CyNNKoi0U0W9Wyk0Uq1l47vDWu9iNdpWU4WfFQxmh9gWiGfSLld-TT002pPaLG9Aa50DaBw0lLxd_m2mM839Zmthu1gGm00000miPbl-WCA-0DWu20G8aE_o7zzdNWvDJnXe3bXEZxCw0Em8Gzs0u1eGznh8lRQ03mFvF1bXd840pu41g04HQ84GEG4G6O4O0ZeH5dP3mNN3ZMO3-n4h3SbVkwwE8_y18Q0G6e4_ppYe-6kwsE5k0JiBOye1ImjZoe5F3LxG7Kllds1UWK3CWLk_YGx-06q1NuXiBt1TWLmOhsxAEFlFnZy9WMq9-QzmMW5j2Kl_S5oHRG5fZmthu1WHUO5vkfZIYe5md05mpO5y24FPaO00000000y3yQ03JaY3-ovh8zFt_c5LnmWdQR33xsENo0HJmWFvVhqdC1GCY0h_QnIG3HRoHk6bK4E0HiR6WoWc2US_3Q6JOQeeudvW6QWBhgmJ64hp9-h4O8F000~1?from=yandex.ru%3Bsearch%26%23x2F%3B%3Bweb%3B%3B0%3B&q=%D0%B1%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE+%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD&etext=2202.1pQ6ACz-Lysc88ObOsXOzsYRm8K6j42wxsyFgZF-Pzq21zX0NVI9uCwDNWN052_0endnYWx3ZW1haXduc3VqeQ.810fee79644d1eb772307ca8a2b2d7d553f09b48&baobab_event_id=kbz2gokqsp
#2 http://yabs.yandex.ru/count/WaKejI_zOEq1tH40H1v4iDdQfR6mkmK0xG8GWX0n6v7uNW00000uh8f50d32wAcI2801fOYFT8W1dyMDzKwG0SR2rER4W8200fW1niBKvaIu0UJ2hi4Vm05Ss07Ih-WVu07uZfuVw0600Q02fhJV5TW20l02w9F8Z0wO0ygU8ExA0lW4dwQa0OW5dwQa0P05yDNj0Q05WP0og0NMuYcm1TRYARW5iBOym0NmrUq1o0MmjZoYjh7e1Q06ZW-e1euFoGOLIVFk_TX3XD465TqePlxOGuJP1W00011w0000gGTxaRJxqMnrCh07W82OBBW7j0Rn1-JOE2R5vyu7X8AJskyAoQeB481FUwXxaG00QTmgL2If1G3P2-WBdwQa0V0B1OWCcF3UlW6f30000032ncM_w0mhu0s3W810YGxxN6t5_hBfbPBDzzwVzg7OSQoBssW0y3-JmPOPo10C-10QW14Mc1608w4HPsGy5rmurc0_iHAmt9NxkkZYF_0I6W41g1FVySRz-hojZXRW4x2sFA0KiBOyg1JmrUq1rBxvzWNe50p85RluaE_W1j0L-8R2zmNO5S6AzkoZZxpyO_2O5j2VclS5e1RGbB_t1SaMq1QOyDw-0O4Nc1URgOqeg1S9m1SCs1V0X3sP600000000F0_6m0qv8W_ikQoFKL_vdLSS89simm-9Zfyu4Kyy9-hCqm4VAUN0O0GmrURWMLN7SkHc02YtqZSDge8S0ZOMD5a13tdEKDI3z04v5MFJY5zbV73DKBa0G00~1?from=yandex.ru%3Bsearch%26%23x2F%3B%3Bweb%3B%3B0%3B&q=%D0%B1%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE+%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD&etext=2202.N7Qgb7r4JOxk0NPIO-GYR7BkDI9E5o2hC6T6SobgxlFOhjhRwCyoI_IC-HZMv2_5d2ZoZWR0Ynlrc2F4dnF6cQ.968d00421305cb1b3089df8f4d43b7d2c51563c7&baobab_event_id=kbz2hl6oi1
#3 http://yabs.yandex.ru/count/WZeejI_zOEW1XH4091r3zk-7IeApwWK0w08GWX0nDv7uNW00000u109mmkYfaWY00QM8ZtI80P_5ZVLEa076mjJcn820W0AO0SR2rEP4k07amgx17y01NDW1qg_e7-01-8wU7-W1W06W0gQqtnNO0WBm0eopxz86c0FAdY2W0mRGXWFu1DNkVuW5rUv_a0NmrUq1e0MSWIUe1OB18B05Wi4Wk0MmjZp01V3LxG781R2sFAAsiUW5e0QE3wW6ZW_91Z4XPD0j5WT8qGOnjPb7BXO7I0FxUcptUtDrCh07W82O3BW7j0Rn1-JOE2R5vyu7X8AJskyAoQeB4DqPvKJxUW00N5lLLIIf1G3P2-WBrUv_y0i5Y0oOyDw-0QaC00000CB6PR_e32lW3OE0W4293lyX_VPruEInmf23tSN5WzXnh8lRQ03mFvF1bXaQW14Mc17ZimQX4MTaF1TSEDPWFx4IiDoL-xheuZ_m4Xe10QWJe-Ez_EAzhOuMu1EmjZoW5B2sFAWKyDNjrBxvzWNe50p85RluaE_W1j0L-8R2zmNO5S6AzkoZZxpyO_2O5j3bfFS5e1RGbB_t1SaMq1QOyDw-0O4Nc1URgOqeg1S9m1SCs1V0X3sP600000000F0_7W0qv90_ikQoFSAWUbMuO0gQU3Bu-EVmGHRnW7wkZXiHOk8b24000480Nsq6bi7BRCHD0eX-8t7Jg2B08M3Z7pW4mJnd04q4D3hm4_C0JK1TzU0OmbSPFrOZ11u0~1?from=yandex.ru%3Bsearch%26%23x2F%3B%3Bweb%3B%3B0%3B&q=%D0%B1%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE+%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD&etext=2202.6kFeBMp-FST5zuJaLLJG5yw30mg45760_dxL2WJPT4Rr2WIpyVTHMUngPtczN73da2VkcXp0YmZrdXR5Y291eg.1967950f9f29bb20f08560f4bb079e99e4bd02d9&baobab_event_id=kbz2iemv91