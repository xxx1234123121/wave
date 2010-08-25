#!/usr/bin/env python
import os

from datetime import datetime

print datetime.now().strftime('%Y-%m-%d %H:%M:%S')+' executing cronHFRadar.py'
os.system('python ../py/bin/getHFRadar.py -v 38 42 -128 -123 "2000-01-01 00:00:00" "'+datetime.now().strftime('%Y-%m-%d %H:00:00')+'" 6km >> cron.log')
#print('python ../py/bin/getHFRadar.py -v 38 42 -128 -123 "2000-01-01 00:00:00" "'+datetime.now().strftime('%Y-%m-%d %H:00:00')+'" 6km >> cron.log')
