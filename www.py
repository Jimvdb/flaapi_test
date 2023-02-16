from flask import Flask

print("open file")
fl_www = Flask(__name__)


@fl_www.route("/")
def index2():
    return "Hello from www.py!"


def start_fl():
    print("start")
    fl_www.run(port=5000)


class WWW:

    def __init__(self):
        print("Thread www")

    def start(self):
        start_fl()


