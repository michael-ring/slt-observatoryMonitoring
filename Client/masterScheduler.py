#!/usr/bin/env python3
import sys

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import locations, telescope
except:
  print("locations configuration is missing in config.py")
  sys.exit(1)

from Common import locationData
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
print(f'Moon Phase is {currentMoonStatus['phase']}')
if currentMoonStatus['alt'] < 0 or currentMoonStatus['phase'] < 15:
  for target in lrgb:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      targetSchedulerData.enableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      targetSchedulerData.enableProject(target['projectname'])
elif currentMoonStatus['alt'] < 40 or currentMoonStatus['phase'] < 40:
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


