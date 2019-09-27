
import pidpy
import time


class MashTun():

    hc = 4184 #joule/kg*C
    heat_loss = 130.0/(67-20) #W/C


    def __init__(self):
        pass
        self.temp = 20  #C
        self.effect = 3500 #Watt
        self.volume = 25
        self.t_air = 20


    def update(self, time_interval, effect):

        t_gain = self.effect*time_interval/(self.volume*self.hc)
        t_loss = (self.temp-self.t_air)*self.heat_loss*time_interval/(self.volume*self.hc)

        new_temp = self.temp + t_gain - t_loss
        self.temp = new_temp
        return new_temp



if __name__ == '__main__':

    ts = 0 #The sample period [seconds]
    kc = 0 #The proportional gain [%/C]
    ti = 0 #The time-constant for the integral gain [seconds]
    td = 0 #The time-constant for the derivative gain [seconds]
    effect = 130.0/(67-20) #3500

    #pid = pidpy.pidpy(ts, kc, ti, td)
    tun = MashTun()

    while True:
        tun.update(1,effect)
        print("t = ", tun.temp)
        time.sleep(1)


