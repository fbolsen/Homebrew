import matplotlib
import kivy
from datetime import datetime
from kivy.clock import Clock
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas, NavigationToolbar2Kivy
from kivy.properties import NumericProperty
#from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt



from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
#import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown

#from matplotlib.transforms import Bbox
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.properties import BooleanProperty

kivy.require('1.9.1')

import temp_logger as tl

accessToken = "6d6873caba909d7f00dde47440fe7933e65582e6"
deviceID = "23001e000947353138383138"



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
        #t_logger.start_loging()

    def stop_log(self):
        print('Stop log')
        #t_logger.stop_logging()


class HomebrewApp(App):

    def build(self):
        print('Build')
        Builder.load_file('HomebrewUI.kv')
        Clock.schedule_interval(self.update,1)
        self.root.ids.bl_plot.add_widget(canvas)


    def update(self, dt): #dt is delta time between each call

        b =self.root.ids.lbl_temp
        if b.text == 'tick':
            b.text = 'tack'
        else:
            b.text = 'tick'


        new_temp = t_reader.temp()
        timestamp = datetime.now()

        t_plot.update_plot(timestamp, new_temp)

    def update_plot(self, dt):
        #update plot
        print('update plot')



t_reader = tl.RandomTemp()
#t_reader = tl.ParticleTempSensor(accessToken, deviceID)
t_plot = tl.LivePlot()
#t_logger = tl.Templogger(source=t_reader, plt=t_plot, freq=30)
canvas = t_plot.canvas



if __name__ == '__main__':

    HomebrewApp().run()