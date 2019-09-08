# Sample Kivy app demonstrating the working of Box layout


# imports

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex as rgb
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot

from numpy import sin
import math
import random
from datetime import datetime, timedelta
import pandas as pd




kv = Builder.load_file('./kivy_graph_test.kv')

def read_temp():
    temp = random.random()
    t = datetime.now()

    return t, temp



class MyBoxLayout(BoxLayout):

    def start(self):
        print('Start')
        Clock.schedule_interval(self.add_temp, 1)

    def stop(self):
        print('Stop')
        Clock.unschedule(self.add_temp)

    def add_temp(self, dt):
        print('add temp')
        t, temp = read_temp()
        print('temp = ', t)
        print('time = ', temp)

        self.ids['temp_graph'].update_plot(t, temp, 20.0)

class MyGraph(Graph):
    def __init__(self, **kwargs):
        super(MyGraph, self).__init__(**kwargs)

        self.plot_window = timedelta(seconds=30)
        self._initdata()
        self._initplot()
        self.temp_min = 20
        self.temp_max = 80
        self.show_setpoint = True

    def set_plot_window(self, s):
        pass

    def _initdata(self):
        N = 10
        timespan = self.plot_window.seconds

        freq_str = str(timespan // N) + 'S'

        self._temp = []
        self._setpoint = []
        self._time = []

        # dt = self.plot_window
        end_time = datetime.now().replace(second=0, microsecond=0)
        start_time = end_time - self.plot_window

        self._time = pd.date_range(start=start_time, periods=N, freq=freq_str).tolist()
        self._temp = [0] * N
        self._setpoint = [0] * N

        self.df = pd.DataFrame(columns=['time', 'temp', 'setpoint'])
        self.df['time'] = pd.date_range(start=start_time, periods=N, freq=freq_str)
        self.df['temp'] = [0] * N
        self.df['setpoint'] = [0] * N
        self.df.index = self.df['time']

    def redraw(self):
        print('redraw')
        self.time_min = self.new_time - self.plot_window
        self.time_max = self.new_time

        self.df_plot = self.df[self.time_min:self.time_max]

        self.plot.points = self.df_plot['temp'].tolist()
        #self.df_plot['time'].tolist())

    def update_plot(self, new_time, new_temp, setpoint=0.0):
        print('Updating plot')

        self.new_time = new_time
        self.new_temp = new_temp

        self._time.append(new_time)
        self._temp.append(new_temp)
        self._setpoint.append(setpoint)

        self.df.loc[new_time] = [new_time, new_temp, setpoint]

        self.redraw()


    def _initplot(self):
        self.label_options = {'color': rgb('#FF0000'), 'bold': True}
        self.background_color = rgb('f8f8f2')
        self.tick_color = rgb('808080')
        self.border_color = rgb('808080')
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.x_ticks_minor = 5
        self.x_ticks_major = 25
        self.y_ticks_major = 1
        self.y_grid_label = True
        self.x_grid_label = True
        self.padding = 5
        self.x_grid = True
        self.y_grid = True
        self.xmin = -0
        self.xmax = 100
        self.ymin = -1
        self.ymax = 1

        self.plot = LinePlot(line_width=4, color=[1, 0, 0, 1])
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        self.add_plot(self.plot)


    def add_datapoint(self, t, temp):
        pass


class GraphTest(App):

    def build(self):
        the_pp = MyBoxLayout()
        return the_pp

    app = MyBoxLayout()


# Instantiate and run the kivy app

if __name__ == '__main__':
    GraphTest().run()