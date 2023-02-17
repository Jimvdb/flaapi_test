# SuperFastPython.com
# example of daemon processes being terminated abruptly
from time import sleep
from multiprocessing import current_process
from multiprocessing import Process


# function to be executed in a new process
def task():
    # get the current process
    process = current_process()
    # report if daemon process
    print(f'Daemon process: {process.daemon}')
    # loop for a while
    for i in range(1000):
        print(i, flush=True)
        # block for a moment
        sleep(0.1)


# entry point
if __name__ == '__main__':
    # create a new daemon process
    process = Process(target=task, daemon=True)
    # start the new process
    process.start()
    # block for a moment to let the daemon process run
    sleep(3)
    # prepare the user
    print('Main process exiting...')