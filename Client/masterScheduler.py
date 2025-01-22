#!/usr/bin/env python3
import sys

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,locations,telescope
from Common import locationData
import targetSchedulerData

currentTime = locationData.getLocationDateTime(locations[telescope['location']])
currentMoonStatus = locationData.getMoonData(locations[telescope['location']])
currentSunStatus = locationData.getSunData(locations[telescope['location']])

if currentSunStatus['alt'] > 0:
  print('Sun is up, exit...')
  logger.info('Sun is up, exit...')
  sys.exit(0)

lrgb = targetSchedulerData.getLRGBTargets()
o2 = targetSchedulerData.getOTargets()

print(f'Moon Altitude is {currentMoonStatus['alt']}')
logger.info(f'Moon Altitude is {currentMoonStatus["alt"]}')
print(f'Moon Magnitude is {currentMoonStatus['mag']}')
logger.info(f'Moon Magnitude is {currentMoonStatus["mag"]}')
print(f'Moon Phase is {currentMoonStatus['phase']}')
logger.info(f'Moon Phase is {currentMoonStatus["phase"]}')
if currentMoonStatus['alt'] < 0 or currentMoonStatus['phase'] < 15:
  for target in lrgb:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      logger.info(f'Enable {target["projectname"]}')
      targetSchedulerData.enableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      logger.info(f'Enable {target["projectname"]}')
      targetSchedulerData.enableProject(target['projectname'])
elif (currentMoonStatus['alt'] < 40 and currentMoonStatus['phase'] < 70) or currentMoonStatus['phase'] < 40:
  for target in lrgb:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      logger.info(f'Disable {target["projectname"]}')
      targetSchedulerData.disableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 2:
      print(f'Enable  {target['projectname']}')
      logger.info(f'Enable {target["projectname"]}')
      targetSchedulerData.enableProject(target['projectname'])
else:
  for target in lrgb:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      logger.info(f'Disable {target["projectname"]}')
      targetSchedulerData.disableProject(target['projectname'])
  for target in o2:
    if target['projectstate'] == 1:
      print(f'Disable {target['projectname']}')
      logger.info(f'Disable {target["projectname"]}')
      targetSchedulerData.disableProject(target['projectname'])

print()
targets = targetSchedulerData.getEnabledTargets()
for target in targets:
  print(f'{target['projectname']} is enabled')
  logger.info(f'{target["projectname"]} is enabled')
print()
targets = targetSchedulerData.getDisabledTargets()
for target in targets:
  print(f'{target['projectname']} is disabled')
  logger.info(f'{target["projectname"]} is disabled')
