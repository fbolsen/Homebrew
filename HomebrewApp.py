from kivy.app import App

from kivy.config import Config
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '900')

from kivy.core.window import Window

from kivy.graphics import Color
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex as rgb
from kivy.properties import NumericProperty, BoundedNumericProperty, ObjectProperty, \
    StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy_garden.graph import Graph, LinePlot, MeshLinePlot
#from kivy.garden.knob import Knob
from kivy.uix.checkbox import CheckBox

# todo: add logging

from datetime import datetime, timedelta
import pandas as pd
from numpy import sin
from random import random


import time
import json
import re

USE_MPL = False
if USE_MPL:
    import matplotlib
    matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')

import temp_logger as tl

import threading

from simple_pid import PID
from pidpy import pidpy

import BrewController as BC
#todo det ser ut som udatePIDInt styrer oppderingsfrekvensen for plot
updatePIDInt = 1


credentials_fn = "particle credentials.json"
credentials = tl.read_credentials()
accessToken = credentials["accessToken"]
deviceID = credentials["deviceID"]
# = '/dev/tty.usbmodem14301'
port = '/dev/tty.usbmodem14501'
#controller = BC.Particle()
#controller = BC.Simulator()
#controller = BC.ParticleSerial()
#controller = object()



# This is the widget for controlling the setpoint manually
# The GUI is defined in the .kv file


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)

class MyGraph(Graph):
    def __init__(self, **kwargs):
        super(MyGraph, self).__init__(**kwargs)

        self.plot_window = timedelta(seconds=300)
        self._initdata()
        self._initplot()
        self.temp_min = 20
        self.temp_max = 80

    def set_plot_window(self, s):
        pass

    def _initdata(self):
        N = 100
        self._num_datapoints = N
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
        #print('redraw')
        self.time_min = self.new_time - self.plot_window
        self.time_max = self.new_time

        #self.df_plot = self.df[self.time_min:self.time_max]
        #y = self.df['temp'][:-100].tolist()
        N = self._num_datapoints
        x = [x for x in range(0, N)]
        plot_data = list(zip(x, self._temp[-N:]))
        self.plot.points = plot_data

        if self.show_setpoint:
            setpoint_data = list(zip(x, self._setpoint[-N:]))
            self.setpoint_plot.points = setpoint_data



        #self.df_plot['time'].tolist())

    def update_plot(self, new_time, new_temp, setpoint=0.0):
        #print('MyGraph::Updating plot')

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
        self.y_ticks_major = 10
        self.y_grid_label = True
        self.x_grid_label = True
        self.padding = 5
        self.x_grid = True
        self.y_grid = True
        self.xmin = -0
        self.xmax = self._num_datapoints
        self.ymin = 20
        self.ymax = 80
        self.show_setpoint = True

        self.plot = LinePlot(color=[0, 0, 1, 1], line_width=2) #, color=[1, 0, 0, 1])
        x = [x for x in range(0,101)]

        y = [random() for x in range (0,101)]
        #self.plot.points  = [(x, random()) for x in range(0, 101)]
        plot_data = list(zip(x, self._temp))
        #plot_data = list(zip(self._time, self._temp))

        self.plot.points = plot_data
        self.add_plot(self.plot)

        if self.show_setpoint:
            self.setpoint_plot = LinePlot(color=[1, 0, 0, 1], line_width=2) #, color=[1, 0, 0, 1])
            self.setpoint_plot.points = plot_data
            self.add_plot(self.setpoint_plot)

    def add_datapoint(self, t, temp):
        pass


class TempWidget(BoxLayout):
    temp = BoundedNumericProperty(0, min=0, max=200)
    setpoint = BoundedNumericProperty(20, min=10, max=100)

    def update_temp(self, t):
        self.temp = t

    def up(self):
        print('up')
        try:
            self.setpoint = self.setpoint + 1
        except:
            pass
        print(self.setpoint)

    def down(self):
        print('down')
        try:
            self.setpoint = self.setpoint - 1
        except:
            pass
        print(self.setpoint)

class PID_C_Widget(BoxLayout):
    # kc, ti, td
    kc = NumericProperty()
    ti = NumericProperty()
    td = NumericProperty()

    def update_kc(self):
        self.kc = self.ids.sl_kc.value
        pid.kc = self.kc

    def update_ti(self):
        self.ti = self.ids.sl_ti.value
        pid.ti = self.ti

    def update_td(self):
        self.td = self.ids.sl_td.value
        pid.td = self.td

    def pid_reset(self):
        self.ids.lbl_kc.text = "{0:.6g}".format(settings["k_c"])
        self.ids.sl_kc.value = settings["kc"]
        self.ids.lbl_ti.text = "{0:.6g}".format(settings["t_i"])
        self.ids.sl_ti.value = settings["t_i"]
        self.ids.lbl_td.text = "{0:.6g}".format(settings["t_d"])
        self.ids.sl_td.value = settings["t_d"]

class PIDWidget(BoxLayout):
    Kp = NumericProperty()
    Ki = NumericProperty()
    Kd = NumericProperty()

    def update_Kp(self):
        self.Kp = self.ids.sl_Kp.value
        pid.Kp = self.Kp

    def update_Ki(self):
        self.Ki = self.ids.sl_Ki.value
        pid.Ki = self.Ki

    def update_Kd(self):
        self.Kd = self.ids.sl_Kd.value
        pid.Kd = self.Kd

    def pid_reset(self):
        self.ids.lbl_Kp.text = "{0:.6g}".format(settings["Kp"])
        self.ids.sl_Kp.value = settings["Kp"]
        self.ids.lbl_Ki.text = "{0:.6g}".format(settings["Ki"])
        self.ids.sl_Ki.value = settings["Ki"]
        self.ids.lbl_Kd.text = "{0:.6g}".format(settings["Kd"])
        self.ids.sl_Kd.value = settings["Kd"]


class TimeWidget(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'time'
        # self.start_time = 0
        print(self.mode)

    def start(self):
        self.start_time = datetime.now()
        print('start time: ', self.start_time)

    def update(self):
        if self.mode == 'time':
            self.ids.lbl_time.text = datetime.now().strftime("%H:%M:%S")
        elif self.mode == 'elapsed':
            # print(self.start_time)
            elapsed = datetime.now() - self.start_time
            self.ids.lbl_time.text = str(elapsed).split(".")[0]

        else:
            print('mode unkown')

    def set_mode(self, text):
        print('mode:', text)
        self.mode = text


class PWMWidget(BoxLayout):
    power = BoundedNumericProperty(0, min=0.0, max=100.0)
    periode = BoundedNumericProperty(10.0, min=5.0, max=20.0)
    #color = ListProperty([1, 1, 0])
    #override = BooleanProperty(False)
    override = False

    def update_power(self):
        self.power = self.ids.sl_power.value

    def start(self, power=0):
        print('Starting pwm. Power = ', power)

    def stop(self):
        print('Stopping pwm')
        pass

    def toggle(self):
        print('toggle_override: ', self.ids.chk_override.active)
        self.override = self.ids.chk_override.active



class Homebrew(BoxLayout):
    temp_widget = ObjectProperty(None)
    pid_widget = ObjectProperty(None)
    pwm_widget = ObjectProperty(None)
    time_widget = ObjectProperty(None)
    app_mode = StringProperty(None)

    def __init__(self, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        self.temp = 0
        self._updateTempInt = 2
        self.add_mode = 'Simulation mode'
        Clock.schedule_once(self.update_txt, 0.1)
        self.isRunning = False
        self.connected = False
        self._power = 0

    def update_txt(self, *args):

        # self.ids.pid_w.ids.lbl_Kp.text = "{0:.6g}".format(settings["Kp"])
        # self.ids.pid_w.ids.sl_Kp.value = settings["Kp"]
        # self.ids.pid_w.ids.sl_Kp.min = settings["Kp_min"]
        # self.ids.pid_w.ids.sl_Kp.max = settings["Kp_max"]
        #
        # self.ids.pid_w.ids.lbl_Ki.text = "{0:.6g}".format(settings["Ki"])
        # self.ids.pid_w.ids.sl_Ki.value = settings["Ki"]
        # self.ids.pid_w.ids.sl_Ki.min = settings["Ki_min"]
        # self.ids.pid_w.ids.sl_Ki.max = settings["Ki_max"]
        #
        # self.ids.pid_w.ids.lbl_Kd.text = "{0:.6g}".format(settings["Kd"])
        # self.ids.pid_w.ids.sl_Kd.value = settings["Kd"]
        # self.ids.pid_w.ids.sl_Kd.min = settings["Kd_min"]
        # self.ids.pid_w.ids.sl_Kd.max = settings["Kd_max"]

        pass

    def connect(self):
        print('App mode = ', self.app_mode)
        print('Attempting to connect!')

        message = ''
        result = False


        if self.app_mode == 'Simulation mode':
            controller = BC.Simulator(mode='kettle')
            result, message = controller.connect()
            print('Result: ', result)
            print('Message: ', message)
            if result == True:
                self.controller = controller
                self.connected = True

        elif self.app_mode == 'Particle cloud':
            controller = BC.ParticleCloud()
            print("Trying to connect to controller with accesstoken {} and deviceID {}".format(accessToken, deviceID))
            result, messsage = controller.connect(accessToken=accessToken, deviceID=deviceID)
            if result == True:
                print('Result: ', result)
                print('Message: ', message)
                self.connected = True
                self.controller = controller
                controller.power = 50
                controller.period = 1000
            else:
                print("Not able to connect!")
                print('Result: ', result)
                print('Message: ', message)
                self.connected = False

        elif self.app_mode == 'USB/serial':
            controller = BC.ParticleSerial()
            result, message = controller.connect(port=port)
            if result == True:
                self.connected = True
                self.controller = controller
                # controller.power = 0
                # controller.period = 1000
            else:
                print("Not able to connect!")
                print('Result: ', result)
                print('Message: ', message)
                self.connected = False

        else:
            raise Exception('Unknown app mode: ', self.app_mode)


        #
        # #todo start checking connection heartbeat
        #
        # if self.connected == True:
        #     btn = self.ids['btn_connect']
        #     btn.background_color = [0,1,0,1]
        #     #btn.text = 'Disconnect ...'


    def set_ymax(self, control,  txt):
        print('set_ymax: ', txt)
        self.ids.temp_graph.ymax = float(txt)


    def set_ymin(self,control, txt):
        print('set_ymin: ', txt)
        self.ids.temp_graph.ymin = float(txt)

    def start_mash(self):
        # todo: enable time widget on start

        if not self.isRunning:
            result = self.controller.start()
            log.start_logging()
            print('Start result = ', result)
            self.isRunning = True
            self.ids.time_w.start_time = datetime.now()
            print('Starting mash at: ', self.ids.time_w.start_time)
            #todo Clock waits for the function to return.
            Clock.schedule_interval(self.update, updatePIDInt)
        else:
            print('Already running!')

    def stop_mash(self):
        # todo disable time widget on stop

        if self.isRunning:
            result = self.controller.stop()
            print('Stop result = ', result)
            self.stop_time = datetime.now()
            print('Stoping mash at: ', self.stop_time)
            self.isRunning = False
            #todo: stop the pid thread
        else:
            print('Not running!')

    def _update(self):

        #print('Starting _update')
        start = time.time()
        if self.app_mode == 'Particle USB/Serial':
            t = self.controller.readTemp()
            print('T = ', t)
            self.temp = t
        elif self.app_mode == 'Simulation mode':
            t = self.controller.readTemp(pwr=self._power, dt=updatePIDInt)
            self.temp_widget.update_temp(t)
            self.temp = t
            print('T = ', t)
        else:
            result = self.controller.updateTemp()
            t = self.controller.readTemp()
            if t != -127:
                self.temp_widget.update_temp(t)
                self.temp = t
            else:
                print('t = ', t)
            #print('t = ', t)

        setpoint = self.temp_widget.setpoint

        if PID_TYPE =='SIMPLE':
            pid.setpoint = setpoint
            power = int(pid(self.temp))
        elif PID_TYPE =='type_C':
            power = pid.calcPID_reg4(self.temp,setpoint, enable=True)

        self._power = power

        #print('------------')
        #print(self.pwm_widget.override)
        if self.pwm_widget.override:
            power = self.pwm_widget.power
            print('Power =  ', power)
            self.controller.power = power
        else:
            #power = int(pid(self.temp))
            print("power: ", power)
            self.pwm_widget.power = power
            self.controller.power = power

        timestamp = datetime.now()

        comment = 'comment'
        log.write_to_log(timestamp, t, setpoint, power, comment)

        if USE_MPL:
            t_plot.update_plot(timestamp, self.temp, setpoint)
        else:
            self.ids['temp_graph'].update_plot(timestamp, self.temp, setpoint)


        end = time.time()
        #print('Update duration: ', end - start)


    def update(self, dt):
        update_thread = threading.Thread(name='Update', target=self._update)
        #print('starting thread')
        update_thread.start()
        #print('Returned from thread')

    def update_time(self, dt):
        self.ids.time_w.update()

    def updateTemp(self, dt):
        #('update_temp')
        tempThread = threading.Thread(name='TempThread', target=self._updateTemp())
        tempThread.start()

    def _updateTemp(self):
        #('_updateTemp')
        #print('Calling update temp)')
        if self.app_mode != 'Particle USB/Serial':
            result = self.controller.updateTemp()
        #print('Calling readTemp')
        t = self.controller.readTemp()
        if t != -127:
            #self.temp_widget.update_temp(t)
            self.temp = t
        else:
            pass
            #print('t = ', t)
        #print('t = ', t)

    def auto_scale(self, instance, value):

        if value is True:
            print("Switch On")
        else:
            print("Switch Off")

    def change_appmode(self, txt):
        print('change_appmode:', txt)

        if txt == 'Simulation mode':
            pass
        elif txt == 'Particle cloud':
            pass
        elif txt == 'Particle USB/Serial':
            pass

        self.app_mode = txt


class HomebrewApp(App):
    def build(self):
        grey = (0.5, 0.5, 0.5, 1)
        Window.clearcolor = grey
        app = Homebrew()
        # time_w = TimeWidget()
        # This starts the update process at each tick. The app.update function starts a new thread
        # so that the process in non-blocking
        #Clock.schedule_interval(app.update, update_interval)
        Clock.schedule_interval(app.update_time, 1)
        if USE_MPL:
            app.ids.bl_plot.add_widget(canvas)

        return app

    def on_start(self):
        print('on_start')
        # print(self.root.ids)
        # self.root.ids["sl_Kp"].value = 33

    def on_stop(self):
        print('On Stop!!')
        print("Stopping the controller!")
        self.controller.stop()
        #todo do more tidying up when closing the app




def read_settings(fn):
    with open(fn) as f:
        params = json.load(f)
    return params  # (tunings["Kp"], tunings["Ki"], tunings["Kd"])




if __name__ == '__main__':

    #todo add option for simulator mode
    if USE_MPL:
        t_plot = tl.LivePlot()
        canvas = t_plot.canvas
    else:
        pass

    log = tl.LogFile()

    PID_TYPE = 'SIMPLE'

    settings_fn = "settings.json"


    if PID_TYPE == 'SIMPLE':
        print("PID_TYPE = ", PID_TYPE)
        #settings_fn = "settings.json"
        settings = read_settings(settings_fn)["simple_pid"]

        pid_tunings = ((settings["Kp"], settings["Ki"], settings["Kd"]))

        pid = PID()
        pid.sample_time = updatePIDInt # settings["sample_time"]
        pid.output_limits = (0, 100)
        pid.tunings = pid_tunings
        pid.setpoint = 20.0

        print(pid.tunings)

    elif PID_TYPE == 'TYPE C':
        print("PID_TYPE = ", PID_TYPE)
        settings = read_settings(settings_fn)["type_c"]

        pid = pidpy(ts=updatePIDInt,
                    kc=settings['kc'],
                    ti=settings['ti'],
                    td = settings['td'],
                    )



    else:
        raise ValueError("Unknown PID type: " + PID_TYPE)

    HomebrewApp().run()
