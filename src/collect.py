from clickbot import DefaultDriver, TorDriver
import time

kw = [
    'банкротство юридических лиц обнинск',
    'банкротство граждан',
]

while True:
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
    time.sleep(300)