import threading
import json
import requests
import random
import time
import math

from abc import ABCMeta , abstractmethod


MIN_PERIOD = 1000 #in ms
MAX_PERIOD = 10000 #in ms
DEFAULT_PERIOD = 2000 #in ms

MIN_POWER = 0 #in percent
MAX_POWER = 100

BASE_URL = "https://api.spark.io/v1/devices"

class BaseClass(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, accessToken='', deviceID=''):
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


class Particle():


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

        #read the credentials
        self._accessToken = accessToken
        self._deviceId= deviceID


        #get device information
        url = BASE_URL + '/' + self._deviceId
        payLoad = {"access_token": self._accessToken, "format": "raw"}
        answer = requests.get(url, params=payLoad).json()




        #parse the result
        if answer['connected']:
            variables =  {'period': 'int32', 'dutyCycle': 'int32', 'dutyCycleMillis': 'int32', 'tempC': 'double', 'doPWM': 'int32'}
            functions= ['setPeriod', 'setDutyCycle', 'Start', 'Stop', 'RequestTemp']
            actual_variables = answer['variables']
            acttual_functions = answer['functions']

            if all (v in variables for v in actual_variables):
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


        allOK = variablesOK and functionsOK  and connectedOK
        print('allOK = ', allOK)


        return allOK


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

        url = "https://api.spark.io/v1/devices/" + self._deviceId + "/" + funcName
        payLoad = {"access_token": self._accessToken, "params": params}

        print('Calling function ', funcName)
        print('Params :', params)
        #print('URL :', url)

        answer = requests.post(url, data=payLoad)
        #print(answer.text)


        if not answer.ok:
            raise ValueError()
            print(answer.text)

        return answer

    def __readVariable(self, varName=''):

        baseUrl = "https://api.spark.io/v1/devices"
        url = baseUrl + '/' + self._deviceId + '/' + varName

        #print('Reading variable ', varName)
        #print('URL :', url)

        payLoad = {"access_token": self._accessToken, "format": "raw"}

        answer = requests.get(url, params=payLoad).json()

        return answer

    @property
    def is_connected(self):
        #todo add code to check if particle is connected
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

    def __init__(self):

        self._accessToken = ''
        self._deviceId = ''
        self._connected = False
        self._running = False
        self._period = DEFAULT_PERIOD
        self._power = MIN_POWER

    def connect(self, accessToken='', deviceID=''):

        time.sleep(1)
        return True

    def updateTemp(self):
        return {'ok':True}

    def readTemp(self):

        period = 20
        amplitude = 5
        base = 30

        phase = math.remainder(time.time(), period) / period
        sin = math.sin(2*math.pi*phase)

        result = base + amplitude*phase
        self._temp = result
        return result

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

