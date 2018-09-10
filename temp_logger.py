import time
from time import gmtime, strftime
from datetime import datetime, timedelta
import threading
import random
import sys
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json

def read_credentials():
    with open('particle credentials.json') as f:
        data = json.load(f)
    return data

class LivePlot():

    def __init__(self):
        self.plot_window = timedelta(seconds=30)
        self._initdata()
        self._initplot()
        self.temp_min= 20
        self.temp_max = 80


    def set_plot_window(self, s):
        self.plot_window = timedelta(seconds=s)


    def _initdata(self):
        N = 10
        timespan =  self.plot_window.seconds

        freq_str = str(timespan // N) + 'S'

        self._temp = []
        self._time = []

        # dt = self.plot_window
        end_time = datetime.now().replace(second=0, microsecond=0)
        start_time = end_time - self.plot_window

        self._time = pd.date_range(start=start_time, periods=N, freq=freq_str).tolist()
        self._temp = [0] * N

        self.df = pd.DataFrame(columns=['time', 'temp'])
        self.df['time'] = pd.date_range(start=start_time, periods=N, freq=freq_str)
        self.df['temp'] = [0] * N
        self.df.index = self.df['time']



    def _initplot(self):

        self.fig, self.ax = plt.subplots()
        self.canvas = self.fig.canvas
        # self.ax.plot(self._time, self._temp)
        self.line, = self.ax.plot(self._time, self._temp, lw=2)


    def redraw(self):

        self.time_min = self.new_time - self.plot_window
        self.time_max = self.new_time

        self.ax.set_xlim(self.time_min, self.time_max)
        self.ax.set_ylim([self.temp_min, self.temp_max])

        #self.line.set_xdata(self._time)
        #self.line.set_ydata(self._temp)
        ##self.line, = self.ax.plot(self._time, self._temp, lw=2,)

        #self.line.set_xdata(self.df['time'][self.time_min:self.time_max])
        #self.line.set_ydata(self.df['temp'][self.time_min:self.time_max])

        self.df_plot = self.df[self.time_min:self.time_max]
        #print(df_plot)
        self.line.set_xdata(self.df_plot['time'].tolist())
        self.line.set_ydata(self.df_plot['temp'].tolist())

        #self.ax.plot(df_plot['time', df_plot['temp']], lw=2, )

        #print(df_plot)


        self.fig.canvas.draw()


    def update_plot(self, new_time, new_temp):
        print('Updating plot')

        self.new_time = new_time
        self.new_temp = new_temp

        self._time.append(new_time)
        self._temp.append(new_temp)

        self.df.loc[new_time] = [new_time, new_temp]

        self.redraw()


class ParticleTempSensor():

    def __init__(self, access_token, device_id):
        self.__access_token = access_token
        self.__device_id = device_id
        self.__temp = 0
        self.connect()

    def connect(self):
        pass

    def temp(self):
        self.__temp = self.__readTemp()
        return self.__temp

    def __readTemp(self):
        # first update the temp on the sensor
        result = self.__updateTemp()
        baseUrl = "https://api.spark.io/v1/devices"
        url = baseUrl + '/' + self.__device_id + '/temp'
        payLoad = {"access_token": self.__access_token, "format": "raw"}
        return requests.get(url, params=payLoad).json()

    def __updateTemp(self):
        url = "https://api.spark.io/v1/devices/" + self.__device_id + "/update_temp"
        payLoad = {"access_token": self.__access_token, "params": 'dummy'}
        result = requests.post(url, data=payLoad)
        if not result.ok:
            raise ValueError()
            print(result.text)
        return result


# base class to read temp from different sources
class RandomTemp():

    def __init__(self, sleep_time=1.0, mode='random'):
        self.sleep_time = sleep_time

    @staticmethod
    def random_temp(min=0.0, max=100.0):
        return random.random()*(max-min) + min


    def temp(self):
        time.sleep(self.sleep_time)
        return self.random_temp()


class Templogger():

    def __init__(self, freq=1, source=None, plt=None):
        self.freq=freq
        self._t_source = source
        self._plot=plt
        self.log_fn = ''
        self.log_to_file = False


    def stop_logging(self):
        self.log_stop=True
        print('Logging stopped')

    @property
    def plot(self):
        return self._plot

    @plot.setter
    def plot(self, p):
        self._plot = p

    @property
    def t_source(self):
        return self._t_source

    @t_source.setter
    def t_source(self, ts):
        if not isinstance(ts, RandomTemp):
            raise ValueError('ts must be of class Tempreader!')
        else:
            self._t_source=ts

    def start_loging(self, freq=1):

        f = sys.stdout
        self.freq=freq
        self.log_stop=False

        temp_thread = threading.Thread(name='temp_logger', target=self._log_temps)

        if self.log_to_file:
            self.log_fn = strftime("%Y-%m-%dT%H%M%S", gmtime()) + ".csv"
            print('Logging to file: ' + self.log_fn)
            self._write_headers(self.log_fn)

        temp_thread.start()

    def _write_headers(self, fn):

        headers = ['timestamp', 'temp', 'comment']

        with open(fn, mode='w') as f:
            f.write(','.join(headers) + '\n')

    def _log_temps(self):

        while not self.log_stop:
            time.sleep(self.freq)
            #print(time.time())
            t = datetime.now()
            temp = self._t_source.temp()

            if self.log_to_file:
                with open(self.log_fn, mode='a') as f:
                    f.write('{0:%Y-%m-%d %H:%M:%S},{1:.2f}'.format(t, temp) + ',\n')

            print('{0:%Y-%m-%d %H:%M:%S},{1:.2f}'.format(t, temp))

            self._plot.update_plot(t, temp)

        print('read_temps stopping')


