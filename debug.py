import temp_logger as tl
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import json



#myplot = LivePlot()

#while True:
#    new_time = datetime.now()
#    new_temp = 20.0 + random.random()*20.0
#    myplot.update_plot(new_time, new_temp)

#    time.sleep(3)




#read credentials from file
credentials = tl.read_credentials()


my_plot = tl.LivePlot()
my_source = tl.RandomTemp()
my_logger = tl.Templogger(source=my_source, plt=my_plot)

my_logger.start_loging()

time.sleep(60)

my_logger.stop_logging()

