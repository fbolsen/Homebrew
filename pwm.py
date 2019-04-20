# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python

import time, traceback
import threading
import datetime


class PWM:

    def __init__(self, period=5, power=0, levels=10):
        self.period = period
        self.power = power
        self._stop = True
        self.state = 'LOW'
        self.levels = levels
        self._thread = threading.Thread(target=lambda: self.every(self.period, self.duty_cycle))

    def every(self, period, task):
        next_time = time.time() + self.period
        while not self._stop:
            time.sleep(max(0, next_time - time.time()))
            try:
                task()
                self.state = 'LOW'
            except Exception:
                traceback.print_exc()
                # in production code you might want to have this instead of course:
                # logger.exception("Problem while executing repetitive task.")
            # skip tasks if we are behind schedule:
            next_time += (time.time() - next_time) // self.period * self.period + self.period

    def _duty_cycle(self):
        print("duty_cycle: ", str(datetime.datetime.now()), self.power)
        self.state='HIGH'
        time.sleep(self.period*self.power/100.0)
        self.state='LOW'

    def start(self):
        self._stop = False
        #self._thread = threading.Thread(target=lambda: self.every(self.period, self._duty_cycle))
        self._thread.start()

    @property
    def stop(self):
        return self._stop

    @stop.setter
    def stop(self, value):
        if isinstance(value, bool):
            print('Stopping PWM')
            self._stop = value
            self._thread.join()
        else:
            print('PWM.stop must be boolean True or False')
            raise ValueError

    @property
    def is_running(self):
        self._is_running = self._thread.is_alive()
        return self._is_running


