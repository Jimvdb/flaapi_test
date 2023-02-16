from flask import Flask
from fastapi import FastAPI
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import threading

app = Flask(__name__)
api = FastAPI()


@app.route('/config')
def config():
    # Do configuration with Flask
    pass


@api.get('/data')
def get_data():
    # Handle communication with FastAPI
    pass


def serial_communication():
    # Handle serial communication in a separate thread
    pass


if __name__ == '__main__':
    # Start the serial communication thread
    serial_thread = threading.Thread(target=serial_communication)
    serial_thread.start()

    # Combine Flask and FastAPI applications using DispatcherMiddleware
    combined_app = DispatcherMiddleware(app, {
        '/api': api
    })

    # Start the combined application with the specified number of workers
    run_simple('0.0.0.0', 8000, combined_app, threaded=True, processes=1)
