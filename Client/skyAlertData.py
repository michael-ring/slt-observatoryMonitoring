#!/usr/bin/env python3
import sys
from pathlib import Path
from dateutil.parser import parse
import jsonLogHelper
try:
  sys.path.append('.')
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def generateJson():
  _json = getWeatherStatus()
  alljson = jsonLogHelper.appendToDailyLog('weatherdata', _json)
  return alljson


def getWeatherStatus():
  weatherDataFile = Path(telescope['weatherstatusdir']) / "weatherdata.txt"
  weatherStatus = {}
  if weatherDataFile.exists():
    content = weatherDataFile.read_text()
    content = content.split()
    weatherStatus['timestamp'] = str(parse(content[0]+' '+content[1]))
    if content[2] == 'F':
      weatherStatus['skytemp'] = f"{(float(content[4]) - 32) * 5 / 9:.2f}"
      weatherStatus['ambienttemp'] = f"{(float(content[5]) - 32) * 5 / 9:.2f}"
      weatherStatus['sensortemp'] = f"{(float(content[6]) - 32) * 5 / 9:.2f}"
      weatherStatus['dewpoint'] = f"{(float(content[9]) - 32) * 5 / 9:.2f}"
    else:
      weatherStatus['skytemp'] = f"{float(content[4]):.2f}"
      weatherStatus['ambienttemp'] = f"{float(content[5]):.2f}"
      weatherStatus['sensortemp'] = f"{float(content[6]):.2f}"
      weatherStatus['dewpoint'] = f"{float(content[9]):.2f}"
    if content[3] == "M":
      weatherStatus['windspeed'] = f"{int(content[7])*1.609344:.2f}"
    else:
      weatherStatus['windspeed'] = f"{int(content[7]):.2f}"
    weatherStatus['humidity'] = f"{int(content[8]):.2f}"
    weatherStatus['rainflag'] = int(content[11])
    weatherStatus['wetflag'] = int(content[12])
    weatherStatus['cloudcondition'] = int(content[15])
    weatherStatus['windcondition'] = int(content[16])
    weatherStatus['raincondition'] = int(content[17])
    weatherStatus['darknesscondition'] = int(content[18])
  return weatherStatus


if __name__ == '__main__':
  generateJson()
