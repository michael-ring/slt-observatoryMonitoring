#!/usr/bin/env python3
from dateutil import tz
from datetime import datetime,timedelta,time
import requests
import ephem

locations = {
  'Gantrisch' : {
    'latitude': "46.73196228867647",
    'longitude': "7.446461671486496",
    'country': "CH",
    'timezone': ("CH/Zurich"),
    'language': "en",
    'elevation': 1650,
    'locationcode': "gantrisch"
  },
  'Starfront Observatory' : {
    'latitude': "31.547485160577963",
    'longitude': "-99.38248464510205",
    'country': "US",
    'timezone': ("US/Central"),
    'language': "en",
    'elevation': 850,
    'locationcode': "starfront"
  },
  'Prairie Skies Astro Ranch': {
    'latitude': "31.57472",
    'longitude': "-96.44027",
    'country': "US",
    'timezone': ("US/Central"),
    'language': "en",
    'elevation': 173,
    'locationcode': "cdk14"
  }
}


def getLocationDateTime(location):
  return datetime.now(tz=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))


def getSunData(location, overrideDateTime=None):
  sunData={}
  obs = ephem.Observer()
  if overrideDateTime is None:
    obs.date = getLocationDateTime(location)
  else:
    #TODO find correct conversion
    obs.date = overrideDateTime
  obs.lon = location['longitude']
  obs.lat = location['latitude']
  obs.elev = location['elevation']

  obs.pressure = 0
  obs.horizon = '-0:34'

  sunData['rise'] = ephem.localtime(obs.next_rising(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['previousrise'] = ephem.localtime(obs.previous_rising(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['set'] = ephem.localtime(obs.previous_setting(ephem.Sun())).astimezone(tz.gettz(location['timezone']))
  sunData['nextset'] = ephem.localtime(obs.next_setting(ephem.Sun())).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-6'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['twilightrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['twilightset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-12'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['nauticalrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['nauticalset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  obs.horizon = '-18'  # -6=civil twilight, -12=nautical, -18=astronomical
  sunData['astronomicalrise'] = ephem.localtime(obs.next_rising(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))
  sunData['astronomicalset'] = ephem.localtime(obs.previous_setting(ephem.Sun(), use_center=True)).astimezone(tz.gettz(location['timezone']))

  return(sunData)


def getWeatherdata(location):
  try:
    from weatherkitToken import weatherkitToken
  except:
    weatherkitToken = ""
  datasets = "currentWeather,forecastDaily,forecastHourly,forecastNextHour"

  sunData = getSunData(location)

  locationDateTime = getLocationDateTime(location)
  if locationDateTime > sunData['previousrise']:
    start_utc = datetime.combine(locationDateTime, time(hour=12, minute=0, second=0,tzinfo=locationDateTime.tzinfo)).astimezone(tz.gettz('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ")
  else:
    start_utc = (datetime.combine(locationDateTime, time(hour=12, minute=0, second=0,tzinfo=locationDateTime.tzinfo)) - timedelta(hours=-24)).astimezone(tz.gettz('UTC')).strftime("%Y-%m-%dT%H:%M:%SZ")
  url = f"https://weatherkit.apple.com/api/v1/weather/{location['language']}/{location['latitude']}/{location['longitude']}?dataSets={datasets}&countryCode={location['country']}&timezone={location['timezone']}&hourlyStart={start_utc}"
  response = requests.get(url, headers={'Authorization': f'Bearer {weatherkitToken}'})
  weatherdata=response.json()
  weatherdata['currentWeather']['asOf'] = datetime.strptime(weatherdata['currentWeather']['asOf'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))

  for index in range(len(weatherdata['forecastHourly']['hours'])):
    forecastStart = datetime.strptime(weatherdata['forecastHourly']['hours'][index]['forecastStart'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz(location['timezone']))
    weatherdata['forecastHourly']['hours'][index]['forecastStart'] = forecastStart

  return weatherdata