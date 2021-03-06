import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import matplotlib.pyplot as plt

import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
#import kivy
#from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas, NavigationToolbar2Kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox

#from matplotlib.transforms import Bbox
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.properties import BooleanProperty

kivy.require('1.9.1')


import temp_logger as tl



class MyBoxLayout(BoxLayout):

    #t_reader = tl.Tempreader()
    #t_logger = tl.Templogger(source=t_reader)

    #log_to_file = BooleanProperty()

    def toggle_log(self):

        t_logger.log_to_file = self.ids.chk_log_to_file.active
        print(t_logger.log_to_file)

    def connect(self):
        print('Connect')

    def start_log(self):
        print('Start log')
        t_logger.start_loging()

    def stop_log(self):
        print('Stop log')
        t_logger.stop_logging()


class TestApp(App):

    def build(self):
        print('Build')
        Builder.load_file('/Users/Frode/PycharmProjects/Homebrew/test.kv')
        self.root.ids.bl_plot.add_widget(canvas)


    def update(self, dt): #dt is delta time between each call
        b =self.root.ids.btn_1
        if b.text == 'tick':
            b.text = 'tack'
        else:
            b.text = 'tick'

    def update_plot(self, dt):
        #update plot
        print('update plot')



t_reader = tl.RandomTemp()
t_plot = tl.LivePlot()
t_logger = tl.Templogger(source=t_reader, plt=t_plot)
canvas = t_plot.canvas



if __name__ == '__main__':

    TestApp().run()