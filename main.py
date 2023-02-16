from threading import Thread
from functools import partial
from www import WWW
from api import API
from fapi import FAPI
import time


def fl_www():
    website = WWW()
    website.start()


def fl_api():
    backend = API()
    backend.start()


def fapi():
    fapi = FAPI()
    fapi.start()


def lc_background():
    while True:
        print("start background process")
        time.sleep(5)


if __name__ == '__main__':
    # now to run f and g at a time
    try:
        print("start www")
        Thread(target=partial(fl_www)).start()
    except KeyboardInterrupt:
        pass

    try:
        Thread(target=partial(fl_api)).start()
    except KeyboardInterrupt:
        pass

    try:
        Thread(target=partial(lc_background)).start()
    except KeyboardInterrupt:
        pass

    try:
        Thread(target=partial(fapi)).start()
    except KeyboardInterrupt:
        pass
    # now you can see f and g functions are simultaneously running at the same time
# Deamon script https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
