

class PWM:

    min_period = 1.0
    max_period = 10.0
    min_power = 0.0
    max_power = 100.0

    def __init__(self, period, power, state='low'):
        self.period = period
        self.power = power
        self.state = state



    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, period):
        if period < self.min_period:
            self.__period = self.min_period
        elif period > self.max_period:
            self.__period = self.max_period
        else:
            self.__period = period

    @property
    def power(self):
        return self.__power

    @power.setter
    def period(self, power):
        if power < self.min_power:
            self.__power = self.min_power
        elif power > self.max_power:
            self.__power = self.max_power
        else:
            self.__power = power

    def start(self):
        pass

    def stop(self):
        pass