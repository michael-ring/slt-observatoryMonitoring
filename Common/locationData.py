#!/usr/bin/env python3
from dateutil import tz
from datetime import datetime, timedelta, time
import requests
import ephem
import sys

sys.path.append('.')
sys.path.append('..')
from Common.config import locations

def getLocationDateTime(location):
  return datetime.now(tz=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))


def getSunData(location, overrideDateTime=None):
  sunData = {}
  obs = ephem.Observer()
  if overrideDateTime is None:
    obs.date = getLocationDateTime(location)
  else:
    # TODO find correct conversion
    obs.date = overrideDateTime
  obs.lon = location['longitude']
  obs.lat = location['latitude']
  obs.elev = location['elevation']

  obs.pressure = 0
  obs.horizon = '-0:34'

  sun = ephem.Sun()
  sun.compute(obs)
  sunData['alt'] = int(str(sun.alt).split(':')[0])

  sunData['nextrise'] = ephem.localtime(obs.next_rising(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['previousrise'] = ephem.localtime(obs.previous_rising(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['nextset'] = ephem.localtime(obs.next_setting(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['previousset'] = ephem.localtime(obs.previous_setting(ephem.Sun())).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-6'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['nexttwilightrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previoustwilightrise'] = ephem.localtime(obs.previous_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['nexttwilightset'] = ephem.localtime(obs.next_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previoustwilightset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-12'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['nextnauticalrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previousnauticalrise'] = ephem.localtime(obs.previous_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['nextnauticalset'] = ephem.localtime(obs.next_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previousnauticalset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-18'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['nextastronomicalrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previousastronomicalrise'] = ephem.localtime(obs.previous_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['nextastronomicalset'] = ephem.localtime(obs.next_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['previousastronomicalset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  return sunData


def getMoonData(location, overrideDateTime=None):
  moonData = dict()
  obs = ephem.Observer()
  if overrideDateTime is None:
    obs.date = getLocationDateTime(location)
  else:
    # TODO find correct conversion
    obs.date = overrideDateTime
  obs.lon = location['longitude']
  obs.lat = location['latitude']
  obs.elev = location['elevation']
  moonData['nextrise'] = ephem.localtime(obs.next_rising(ephem.Moon())).astimezone(tz.gettz(location['timezone']))
  moonData['previousrise'] = ephem.localtime(obs.previous_rising(ephem.Moon())).astimezone(tz.gettz(location['timezone']))
  moonData['nextset'] = ephem.localtime(obs.next_setting(ephem.Moon())).astimezone(tz.gettz(location['timezone']))
  moonData['previousset'] = ephem.localtime(obs.previous_setting(ephem.Moon())).astimezone(tz.gettz(location['timezone']))
  moon = ephem.Moon()
  moon.compute(obs)
  moonData['phase'] = moon.phase
  moonData['mag'] = moon.mag
  moonData['alt'] = int(str(moon.alt).split(':')[0])
  return moonData


def getWeatherdata(location):
  try:
    from Common.config import weatherkit
  except:
    print("weatherkit configuration is missing in config.py")
    sys.exit(1)

  datasets = "currentWeather,forecastDaily,forecastHourly,forecastNextHour"

  sunData = getSunData(location)

  locationDateTime = getLocationDateTime(location)
  #if locationDateTime > sunData['previousrise']:
  if sunData['alt'] > 0:
    start_utc = datetime.combine(locationDateTime, time(hour=12, minute=0, second=0, tzinfo=locationDateTime.tzinfo)).astimezone(tz.gettz('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ")
  else:
    if locationDateTime.hour < 12:
      print("Offset -24h")
      start_utc = (datetime.combine(locationDateTime, time(hour=12, minute=0, second=0, tzinfo=locationDateTime.tzinfo)) - timedelta(hours=24)).astimezone(tz.gettz('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
      start_utc = datetime.combine(locationDateTime, time(hour=12, minute=0, second=0, tzinfo=locationDateTime.tzinfo)).astimezone(tz.gettz('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ")
  url = f"https://weatherkit.apple.com/api/v1/weather/{location['language']}/{location['latitude']}/{location['longitude']}?dataSets={datasets}&countryCode={location['country']}&timezone={location['timezone']}&hourlyStart={start_utc}"
  response = requests.get(url, headers={'Authorization': f"Bearer {weatherkit['token']}"})
  weatherdata = response.json()
  weatherdata['currentWeather']['asOf'] = datetime.strptime(weatherdata['currentWeather']['asOf'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))

  for index in range(len(weatherdata['forecastHourly']['hours'])):
    forecastStart = datetime.strptime(weatherdata['forecastHourly']['hours'][index]['forecastStart'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))
    weatherdata['forecastHourly']['hours'][index]['forecastStart'] = forecastStart

  return weatherdata


if __name__ == '__main__':
  getMoonData(locations[telescope['location']], datetime.now())
