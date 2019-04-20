import BrewController
import time
import random

accessToken = "6d6873caba909d7f00dde47440fe7933e65582e6"
deviceID = "23001e000947353138383138"


#p = BrewController.Particle()
p = BrewController.Simulator()

result = p.connect(accessToken=accessToken, deviceID=deviceID)
print('result = ', result)

result = p.start()
print('result = ', result)

result = p.updateTemp()
print('result = ', result)

result = p.readTemp()
print('result = ', result)

p.power = 10

power = p.power
print(power)

p.period = 2000
period = p.period
print(period)

while True:
    result = p.updateTemp()
    #print('result = ', result)
    t = p.readTemp()
    print('temp  = ', t)

    power = random.randint(1,101)
    p.power = power

    time.sleep(2)