from flask import Flask

fl = Flask(__name__)


@fl.route("/")
def index2():
    return "Hello from api.py!"


def start_fl():
    fl.run(port=8080)


class API:
    def __init__(self):
        print("Thread api")

    def start(self):
        start_fl()


