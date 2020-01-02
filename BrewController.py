import json
import requests
import math
import serial
import serial.tools.list_ports
import threading
import ast
import re
import time

from abc import ABCMeta, abstractmethod

MIN_PERIOD = 1000  # in ms
MAX_PERIOD = 10000  # in ms
DEFAULT_PERIOD = 2000  # in ms

MIN_POWER = 0  # in percent
MAX_POWER = 100

BASE_URL = "https://api.particle.io/v1/devices"


class BaseClass(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, accessToken='', deviceID='', port='', timeout=0):
        pass

    @abstractmethod
    def updateTemp(self):
        pass

    @abstractmethod
    def readTemp(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def is_running(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def period(self):
        pass

    @abstractmethod
    def period(self, value):
        pass

    @abstractmethod
    def power(self):
        pass

    @abstractmethod
    def power(self, value):
        pass


class ParticleSerial():

    def __init__(self):

        self._accessToken = ''
        self._deviceId = ''
        self._connected = False
        self._running = False
        self._period = DEFAULT_PERIOD
        self._power = MIN_POWER
        self._temp = 0
        self.listenSerial = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            print('Closing serial connection ', self.serial.name())
            self.serial.close()
        except:
            pass

    def _listener(self):
        print('Starting _listener!')
        while self.serial.is_open:
            self.serial.timeout = 3
            try:
                line = self.serial.readline()
                result = line.decode()
            except:
                print('Listener could not decode : ', line)
            print("Read from serial : ", result)

            # parse the string
            i = result.find("tempC = ")
            if i >= 0:
                try:
                    value = re.findall("-?\d+\.\d+", result)
                    print("Temp = ", value[0])
                    self._temp = float(value[0])
                except ValueError:
                    print('Could not parse: ', result)
                    self._temp = -127.0
            i = result.find("{")
            if i >= 0:
                print("Status : ", result)

    def _find_port(self):
        ports = serial.tools.list_ports.comports()
        port = [i for i in ports if 'Particle' == i.manufacturer]

        if len(port) > 0:
            return port[0].device
        else:
            return ''



    def connect(self, accessToken='', deviceID='', port='', timeout=1):

        if port == '':
            port = self._find_port()
            if port == '':
                raise ValueError('Could not find any USB port!')

        # try:
        print('Attempting to connect to serial: ', port)
        ser = serial.Serial(port=port, timeout=timeout)
        self.serial = ser
        self.serial_name = ser.name
        self.listenSerial = True
        self.serialThread = threading.Thread(name='listener', target=self._listener)
        self.serialThread.daemon = True
        self.serialThread.start()
        print('Successfully connected to : ', ser.name)
        return True, 'All well!'
        # except:
        #    raise Exception('Could not connect to serial port: ', port)

    def __readVariable(self, varName=''):
        cmd = 'get ' + varName + '\r\n'
        self.serial.write(cmd.encode())

        while True:
            line = self.serial.readline()
            result = line.find(varName + '=')
            if result != -1:
                # this means 'varablename=' is found
                # now find =
                startpos = line.find('=')
                value = line[startpos:]
                return float(value)
                break

    def __callFunction(self, funcName='', params=''):
        if len(params) > 0:
            cmd = funcName + '=' + params + '\r\n'
        else:
            cmd = funcName + '\r\n'
        print('Sending command :', cmd)
        self.serial.write(cmd.encode())

    def updateTemp(self):

        try:
            result = self.__callFunction(funcName='requestTemp', params='dummy')
        except:
            raise ValueError()
        return result

    def readTemp(self):
        # result = self.__readVariable(varName='tempC')
        # self._temp = result

        return self._temp

    @property
    def is_connected(self):
        # todo add code to check if particle is connected
        return self._connected

    @property
    def is_running(self):
        return self._running

    def stop(self):
        try:
            self.__callFunction(funcName='Stop', params='dummy')
        except:
            raise ValueError()

        self._running = False

    def start(self):
        if not self._running:
            try:
                self.__callFunction(funcName='start')
                self._running = True
            except:
                raise ValueError()
        else:
            print('Already running!')

    @property
    def period(self):
        result = self.__readVariable(varName='period')
        self._period = result

        return self._period

    @period.setter
    def period(self, value):
        # todo check value boundaries
        strValue = str(value)

        self.__callFunction(funcName='setPeriod', params=strValue)

    @property
    def power(self):
        result = self.__readVariable(varName='dutyCycle')
        self._power = result

        return self._power

    @power.setter
    def power(self, value):

        if 0 <= value <= 100:
            strValue = str(int(value))
            self.__callFunction(funcName='setDutyCycle', params=strValue)
        else:
            raise ValueError


class ParticleCloud():

    def __init__(self):

        self._accessToken = ''
        self._deviceId = ''
        self._connected = False
        self._running = False
        self._period = DEFAULT_PERIOD
        self._power = MIN_POWER
        self._temp = 0

    def connect(self, accessToken='', deviceID=''):

        variablesOK = False
        functionsOK = False
        connectedOK = False
        answer = ''

        # read the credentials
        self._accessToken = accessToken
        self._deviceId = deviceID

        # get device information
        url = BASE_URL + '/' + self._deviceId
        payLoad = {"access_token": self._accessToken, "format": "raw"}
        answer = requests.get(url, params=payLoad).json()

        # parse the result
        if answer['connected']:
            variables = {'period': 'int32', 'dutyCycle': 'int32', 'dutyCycleMillis': 'int32', 'tempC': 'double',
                         'doPWM': 'int32'}
            functions = ['setPeriod', 'setDutyCycle', 'Start', 'Stop', 'RequestTemp']
            actual_variables = answer['variables']
            acttual_functions = answer['functions']

            if all(v in variables for v in actual_variables):
                print('All variables are there')
                variablesOK = True
            else:
                print('All variables are not there')
                variablesOK = False

            if functions == acttual_functions:
                print('All functions are there')
                functionsOK = True
            else:
                print('All functions are not there')
                functionsOK = False

            # even if connected = True it is no guarantee it is since there is a significant timeout
            # connected = False can be trusted, though

            # so we have to read a variable to be sure the device is connected
            # we choose to use 'period'

            url = BASE_URL + '/' + self._deviceId + '/period'
            payLoad = {"access_token": self._accessToken, "format": "raw"}
            result = requests.get(url, params=payLoad).json()

            try:
                period = int(result)
                connectedOK = True
            except:
                # this means result cant be cast to int
                connectedOK = False

        else:
            # this means device is not connected
            connectedOK = False

        allOK = variablesOK and functionsOK and connectedOK
        print('allOK = ', allOK)

        return allOK, answer

    def updateTemp(self):

        try:
            result = self.__callFunction(funcName='RequestTemp', params='dummy')
        except:
            raise ValueError()
        return result

    def readTemp(self):

        # this only reads the variable value
        # to update the temperature reading, call updateTemp first

        result = self.__readVariable(varName='tempC')
        self._temp = result

        return self._temp

    def __callFunction(self, funcName='', params='dummy'):

        url = "https://api.particle.io/v1/devices/" + self._deviceId + "/" + funcName
        payLoad = {"access_token": self._accessToken, "params": params}

        print('Calling function ', funcName)
        print('Params :', params)
        # print('URL :', url)

        answer = requests.post(url, data=payLoad)
        # print(answer.text)

        if not answer.ok:
            raise ValueError()
            print(answer.text)

        return answer

    def __readVariable(self, varName=''):

        baseUrl = "https://api.particle.io/v1/devices"
        url = baseUrl + '/' + self._deviceId + '/' + varName

        # print('Reading variable ', varName)
        # print('URL :', url)

        payLoad = {"access_token": self._accessToken, "format": "raw"}

        answer = requests.get(url, params=payLoad).json()

        return answer

    @property
    def is_connected(self):
        # todo add code to check if particle is connected
        return self._connected

    @property
    def is_running(self):
        return self._running

    def stop(self):

        try:
            self.__callFunction(funcName='Stop', params='dummy')
        except:
            raise ValueError()

        self._running = False

    def start(self):

        if not self._running:
            try:
                self.__callFunction(funcName='Start', params='dummy')
            except:
                raise ValueError()

            self._running = True
        else:
            print('Already running!')

    @property
    def period(self):
        result = self.__readVariable(varName='period')
        self._period = result

        return self._period

    @period.setter
    def period(self, value):
        # todo check value boundaries
        strValue = str(value)

        self.__callFunction(funcName='setPeriod', params=strValue)

    @property
    def power(self):

        result = self.__readVariable(varName='dutyCycle')
        self._power = result

        return self._power

    @power.setter
    def power(self, value):

        if 0 <= value <= 100:
            strValue = str(value)
            self.__callFunction(funcName='setDutyCycle', params=strValue)
        else:
            raise ValueError


class Simulator(BaseClass):
    cp = 4186  # joule per kilogram * degrees

    def __init__(self, mode='kettle'):

        self._accessToken = ''
        self._deviceId = ''
        self._connected = False
        self._running = False
        self._period = DEFAULT_PERIOD
        self._power = MIN_POWER
        self.mode = mode
        self.volume = 25
        self.t_air = 20
        self._temp = 20
        self.loss_factor = 3500 * 0.13 / (67 - 20)  # Joule per sec and C
        self.time_factor = 10

    def connect(self, accessToken='', deviceID=''):

        time.sleep(1)
        self._connected = True
        message = 'Simulator: Connection request succeeded'

        return True, message

    def updateTemp(self):
        return {'ok': True}

    def readTemp(self, dt=1, pwr=0):

        if self.mode == 'sin':
            period = 20  # period in seconds
            amplitude = 5  # AC amplitude
            base = 30  # DC amplitude

            phase = math.remainder(time.time(), period) / period
            value = math.sin(2 * math.pi * phase)

            result = base + amplitude * value
            self._temp = result
            return result
        elif self.mode == 'kettle':
            #temp_gain = pwr * 3500 * dt / (self.cp * self.volume)
            heat_gain = 0.01*pwr*3500*dt*self.time_factor # Joule
            #temp_loss = self.loss_factor * (self._temp - self.t_air) * dt / (self.cp)
            heat_loss = self.loss_factor*(self._temp-self.t_air)*dt*self.time_factor
            delta_temp = (heat_gain-heat_loss)/(self.cp*self.volume)
            print('delta temp = ', delta_temp)
            #temp = self._temp + temp_gain - temp_loss
            temp = self._temp + delta_temp
            #print('temp_gain = ', temp_gain)
            #print('temp_loss = ', temp_loss)
            self._temp = temp
            return temp
        else:
            raise ValueError('Unknown mode: ', self.mode)

    @property
    def is_connected(self):
        return self._connected

    @property
    def is_running(self):
        return self._running

    def stop(self):
        self._running = False

    def start(self):
        self._running = True

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self._power = value


if __name__ == '__main__':
    import time


    def read_credentials(fn):
        with open(fn) as f:
            data = json.load(f)
        return data


    credentials_fn = "/Users/frodebergolsen/Dropbox/PycharmProjects/Homebrew/particle credentials.json"
    credentials = read_credentials(credentials_fn)
    accessToken = credentials["accessToken"]
    deviceID = credentials["deviceID"]

    # BC = ParticleCloud()
    BC = ParticleSerial()
    # result, msg = BC.connect(accessToken=accessToken, deviceID=deviceID)
    # print('Result : ', result)
    # print('Message: ', msg)

    port = "/dev/tty.usbmodem14301"

    result = BC.connect(port=port)
