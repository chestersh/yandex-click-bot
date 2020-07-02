user_agent_catalina = {
    "os": "Windows",
    "os_version": "10",
    "browser": "Firefox",
    "browser_version": "77.0",
    "resolution": "1280x1024",
    "browserstack.local": "false",
    "browserstack.selenium_version": "3.10.0"
}

# import numpy as np
# import scipy.interpolate as si
# from selenium.webdriver.common.keys import Keys
from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import MoveTargetOutOfBoundsException
# import time
#
# # Curve base:
# points = [[0, 0], [0, 2], [2, 3], [4, 0], [6, 3], [8, 2], [8, 0]]
# # points = [[0, 0], [14, 14], [20, 11], [55, 33], [22, 11], [77, 22], [16, 5]]
# points = np.array(points)
#
# x = points[:,0]
# y = points[:,1]
#
#
# t = range(len(points))
# ipl_t = np.linspace(0.0, len(points) - 1, 100)
#
# x_tup = si.splrep(t, x, k=5) # 3
# y_tup = si.splrep(t, y, k=5) # 3
#
# x_list = list(x_tup)
# xl = x.tolist()
# x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]
#
# y_list = list(y_tup)
# yl = y.tolist()
# y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]
#
# x_i = si.splev(ipl_t, x_list) # x interpolate values
# y_i = si.splev(ipl_t, y_list) # y interpolate values
# print(x_i)
# print(y_i)



# from selenium import webdriver
# from bs4 import BeautifulSoup as bs
# from time import sleep
# chrome = webdriver.Chrome()
# chrome.get('https://yandex.ru/search/?lr=967&text=%D0%B1%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE%20%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD')
# sleep(1)
# temp = chrome.page_source

# soup = bs(temp, 'lxml')
# search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
# for i in search_array:
#     print(i.find('div').find('a', rel='noopener'))
#     print(i.find('div').text)
#     print(i.find('div').find('a', rel='noopener').find('b'))
#     print(i.find('div').find('a', rel='noopener').find('span'))
#     print(i.find('div').find('a', rel='noopener').text)
#     print('----')
#     print(chrome.find_element_by_xpath('//*[@id="search-result"]/li[1]/div/div[1]/div[1]/a/b').text)
#     print(chrome.find_element_by_xpath('//*[@id="search-result"]/li[2]/div/div[1]/div[1]/a/b').text)
#
#     break



# def test():
#     with open('training.html', 'r') as file:
#         data = file.read()
#
#     soup = bs(data, 'lxml')
#     search_array = soup.find('div', class_='content__left').find('ul').find_all('li')
#     for i in search_array:
#         print(i.find('div').find('a'))
#         break
# test()
