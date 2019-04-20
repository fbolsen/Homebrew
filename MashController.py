class MashController:

    def __init__(self):
        self._minPeriod = 1 #minimum period in seconds
        self._maxPeriod = 10  # maximum period in seconds
        self._maxDutyCycle = 100
        self._minDutyCycle = 0
        self._isConnected = False
        self._PWMIsRunning = False
        self._period = 10 #period in seconds

        self._tempC = -127
        pass

    def connect(self, deviceID, accessToken):
        pass

    def disconnect(self):
        pass

    @property
    def tempC(self):
        return  self._tempC

    @property
    def isConnected(self):
        return self._isConnected

    @property
    def PWMIsRunning(self):
        return self._PWMIsRunning

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        if value < self._minPeriod:
            pass
        elif value > self._maxPeriod:
            pass
        else:
            self._period = value

    @property
    def dutyCycle(self):
        return self._period

    @dutyCycle.setter
    def dutyCycle(self, value):
        if value < self._minDutyCycle:
            pass
        elif value > self._maxDutyCycle:
            pass
        else:
            self._period = value

    def start(self):
        pass

    def stop(self):
        pass
