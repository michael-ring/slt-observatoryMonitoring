#!/usr/bin/env python3
import sys
from Common import locationData

try:
  from config import locations, telescope
except:
  print("locations configuration is missing in config.py")
  sys.exit(1)

import targetSchedulerData

currentTime=locationData.getLocationDateTime(locations[telescope['location']])
currentMoonStatus=locationData.getMoonData(locations[telescope['location']])
currentSunStatus=locationData.getSunData(locations[telescope['location']])

if currentSunStatus['alt'] >0:
  print('Sun is up, exit...')
  sys.exit(0)

lrgb = targetSchedulerData.getLRGBTargets()
o2 = targetSchedulerData.getOTargets()

print(f'Moon Altitude is {currentMoonStatus['alt']}')
print(f'Moon Magnitude is {currentMoonStatus['mag']}')
if currentMoonStatus['alt'] < 0:
  for target in lrgb:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      targetSchedulerData.enableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      targetSchedulerData.enableProject(target['projectname'])
elif currentMoonStatus['alt'] < 10 :
  for target in lrgb:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      targetSchedulerData.disableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      targetSchedulerData.enableProject(target['projectname'])
else:
  for target in lrgb:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      targetSchedulerData.disableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      targetSchedulerData.disableProject(target['projectname'])

pass


