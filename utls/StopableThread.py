import threading
import time

stop_lock = False


# noinspection PyAttributeOutsideInit
class StopableThread:
    """A thread that loop a function until stop() is called"""
    def __init__(self, func, arg=None):
        self.func = func
        self.arg = arg
        self._stop_lock = False

    def thread_target(self):
        while not self._stop_lock:
            self.func()

    def start(self):
        assert not self._stop_lock, "Thread already started"
        self._stop_lock = False
        self.thread = threading.Thread(target=self.thread_target)
        self.thread.start()

    def stop(self):
        self._stop_lock = True


def func1(*args, **kwargsrgs):
    print(args)
    print(kwargsrgs)


if __name__ == '__main__':
    t1 = StopableThread(func1)
    t1.start()
    time.sleep(5)
    t1.stop()
