import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body

from astropy.time import Time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import datetime
from dateutil import tz
from datetime import datetime, timedelta
import sys

sys.path.append('.')
sys.path.append('..')
from Common.config import locations, telescopes


def getLocationDateTime(_location):
  return datetime.now(tz=tz.gettz('UTC')).astimezone(tz.gettz(_location['timezone']))


def sky_object_plot(_objectra, _objectdec, _location, targetFileName=None):
  width=512
  height=512
  # identify location in geocentric coordinates
  observation_location = EarthLocation.from_geodetic(float(_location['longitude'])*u.deg, float(_location['latitude'])*u.deg, _location['elevation']*u.m)

  print(f"RA: {_objectra} DEC:{_objectdec}")
  print(f"LAT: {observation_location.lat} LON: {observation_location.lon} {_location['locationcode']}")

  start_time = datetime.now(tz=tz.gettz('UTC')).astimezone(tz.gettz(_location['timezone']))
  if start_time.replace(hour=12, minute=0, second=0, microsecond=0) < start_time:
    start_time = start_time.replace(hour=12, minute=0, second=0, microsecond=0)
  else:
    start_time = start_time.replace(hour=12, minute=0, second=0, microsecond=0)  - timedelta(hours=24)

  start_time_utc = start_time.astimezone(tz.gettz('utc'))
  print(start_time)
  # splitting 24h into 10min intervals
  time_int = np.arange(0, 24 * 60, 10) * u.min
  #time_int = np.arange(0, 12 * 60, 10) * u.min
  time = Time(start_time_utc) + time_int
  # define alt-az frame of reference based on the time intervals and geocentric location
  alt_az_conversion = AltAz(obstime=time, location=observation_location)

  # get celestial coordinates for the object of interest (by default in dec-ra system)
  #sky_object = SkyCoord([f"{_objectra} {_objectdec}"], frame="icrs", unit=(u.hourangle, u.deg))
  sky_object = SkyCoord(ra=_objectra*u.hourangle,dec=_objectdec*u.deg, frame="icrs")

  # convert celestial coordinates to our alt-az frame
  sky_object_alt_az = sky_object.transform_to(alt_az_conversion)

  # determine sun position during the time intervals and convert to our alt-az frame
  moon = get_body("moon", time)
  sun = get_body("sun", time)

  moon_alt_az = moon.transform_to(alt_az_conversion)
  sun_alt_az = sun.transform_to(alt_az_conversion)

  moon_alt = moon_alt_az.alt
  sun_alt = sun_alt_az.alt
  object_alt = sky_object_alt_az.alt
  sunset = None
  endcivil = None
  endnautical = None
  endastronomical = None
  beginastronomical = None
  beginnautical = None
  begincivil = None
  sunrise = None

  for i in range(len(sun_alt)):
    if sunset is None and sun_alt[i].value < 0:
      sunset = i
    if endcivil is None and sun_alt[i].value < -6:
      endcivil = i
    if endnautical is None and sun_alt[i].value < -12:
      endnautical = i
    if endastronomical is None and sun_alt[i].value < -18:
      endastronomical = i

  for i in reversed(range(len(sun_alt))):
    if sunrise is None and sun_alt[i].value < 0:
      sunrise = i
    if begincivil is None and sun_alt[i].value < -6:
      begincivil = i
    if beginnautical is None and sun_alt[i].value < -12:
      beginnautical = i
    if beginastronomical is None and sun_alt[i].value < -18:
      beginastronomical = i

  # plotting

  minutes = mdates.drange(start_time_utc, start_time_utc+timedelta(days=1), timedelta(minutes=10))

  px = 1 / plt.rcParams['figure.dpi']
  plt.subplots(figsize=(width * px, height * px))

  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz.gettz(_location['timezone'])))
  plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
  plt.ylim(0, 90)
  plt.xlim(start_time, start_time+timedelta(days=1))

  plt.plot(minutes, moon_alt, color='darkgrey', label='Moon')
  plt.plot(minutes, object_alt, color='black', label='Sky Object')

  plt.axvspan(minutes[sunset], minutes[endcivil], alpha=0.25)
  plt.axvspan(minutes[endcivil], minutes[endnautical], alpha=0.5)
  plt.axvspan(minutes[endnautical], minutes[endastronomical], alpha=0.75)
  plt.axvspan(minutes[endastronomical], minutes[beginastronomical], alpha=1)
  plt.axvspan(minutes[beginastronomical], minutes[beginnautical], alpha=0.75)
  plt.axvspan(minutes[beginnautical], minutes[begincivil], alpha=0.5)
  plt.axvspan(minutes[begincivil], minutes[sunrise], alpha=0.25)
  plt.axhline(60, linewidth=0.5, linestyle='--')
  plt.gcf().autofmt_xdate()
  plt.legend()
  if targetFileName is None:
    plt.show()
  else:
    plt.savefig(targetFileName)
  plt.close()


if __name__ == '__main__':
  objectra = 4.123055555555555
  objectdec = 34.94638888888888
  location = locations[telescopes['slt']['location']]
  sky_object_plot(objectra, objectdec, location)
