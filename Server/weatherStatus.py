#!/usr/bin/env python
from yattag import Doc
from pathlib import Path
from PIL import Image
import platform
import shutil
import subprocess
import sys

try:
  sys.path.append('..')
  sys.path.append('.')
  from Common.config import rootserver,runningOnServer
except Exception as e:
  print(e)
  raise(e)

from Common import locationData


def generateData(locationName):
  location = locationData.locations[locationName]
  weatherData = locationData.getWeatherdata(location)
  sunData = locationData.getSunData(location)
  moonData = locationData.getMoonData(location)

  width, height = 960, 40
  im = Image.new('RGB', (width+40, height))
  ld = im.load()

  for x in range(width):
    if x < int((sunData['previousset'].hour/24+sunData['previousset'].minute/24/60)*width+width/2) % width:
      r, g, b = 128, 128, 255
    elif x < int((sunData['previoustwilightset'].hour*1/24+sunData['previoustwilightset'].minute*1/24/60)*width+width/2) % width:
      r, g, b = 96, 96, 255
    elif x < int((sunData['previousnauticalset'].hour*1/24+sunData['previousnauticalset'].minute*1/24/60)*width+width/2) % width:
      r, g, b = 48, 48, 128
    elif x < int((sunData['previousastronomicalset'].hour * 1 / 24 + sunData['previousastronomicalset'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b = 0, 0, 128
    elif x < int((sunData['nextastronomicalrise'].hour * 1 / 24 + sunData['nextastronomicalrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b = 0, 0,  0
    elif x < int((sunData['previousnauticalrise'].hour * 1 / 24 + sunData['nextnauticalrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b = 0, 0, 128
    elif x < int((sunData['previoustwilightrise'].hour * 1 / 24 + sunData['nexttwilightrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b = 40, 48, 128
    elif x < int((sunData['nextrise'].hour * 1 / 24 + sunData['nextrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b = 96, 96, 255
    else:
      r, g, b = 128, 128, 255

    for y in range(height):
      ld[x+40, y] = r, g, b
  for x in range(40):
    for y in range(40):
      ld[x, y] = 128, 128, 255

  im.save(locationData.locations[locationName]['locationcode'] + '_bg.png')

  doc, tag, text = Doc().tagtext()
  doc.asis(f"<!-- begin include wetter-{locationData.locations[locationName]['locationcode']}.include -->")
  with tag('section'):
    doc.attr(id='content', klass='body')

  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Darkness Info")
    with tag('table'):
      with tag('tr'):
        for title in 'Sunset', 'Twilight', 'Nautical Dark', 'Astronomical Dark', 'Astronomical Dark', 'Nautical Dark', 'Twilight', 'Sunrise':
          with tag('th'):
            text(title)
      with tag('tr'):
        for data in 'previousset', 'previoustwilightset', 'previousnauticalset', 'previousastronomicalset', 'nextastronomicalrise', 'nextnauticalrise', 'nexttwilightrise', 'nextrise':
          with tag('td'):
            text(sunData[data].strftime("%H:%M"))
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Moon Info")
    with tag('table'):
      with tag('tr'):
        for title in 'Previous MoonRise', 'MoonSet', 'MoonRise', 'Next Moonset', 'Phase', 'Magnitude':
          with tag('th'):
            text(title)
      with tag('tr'):
        for data in 'previousrise', 'previousset', 'nextrise', 'nextset':
          with tag('td'):
            text(moonData[data].strftime("%d.%m %H:%M"))
        for data in 'phase', 'mag':
          with tag('td'):
            text(f"{moonData[data]:4.1f}")

  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Current Weather")
    with tag('table'):
      with tag('tr'):
        for title in 'Local Time', 'Cloud Cover', 'High Clouds', 'Mid Clouds', 'Low Clouds', 'Temperature', 'Dew Point', 'Wind Speed', 'Wind Gust':
          with tag('th'):
            text(title)
      with tag('tr'):
        with tag('td'):
          text(weatherData['currentWeather']['asOf'].strftime("%H:%M"))
        with tag('td'):
          text(f"{int(weatherData['currentWeather']['cloudCover']*100)}%")
        with tag('td'):
          text(f"{int(weatherData['currentWeather']['cloudCoverHighAltPct']*100)}%")
        with tag('td'):
          text(f"{int(weatherData['currentWeather']['cloudCoverMidAltPct'] * 100)}%")
        with tag('td'):
          text(f"{int(weatherData['currentWeather']['cloudCoverLowAltPct'] * 100)}%")
        with tag('td'):
          text(f"{round(weatherData['currentWeather']['temperature'])}°C")
        with tag('td'):
          text(f"{round(weatherData['currentWeather']['temperatureDewPoint'])}°C")
        with tag('td'):
          text(f"{round(weatherData['currentWeather']['windSpeed'])}km/h")
        with tag('td'):
          text(f"{round(weatherData['currentWeather']['windGust'])}km/h")

  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Hourly Forecast")
    with tag('table'):
      doc.attr(width='1000px')
      with tag('tr'):
        with tag('th'):
          doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
          text("")
        for hours in range(24):
          forecastHourly = weatherData['forecastHourly']['hours'][0 + hours]
          with tag('th'):
            doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
            text(forecastHourly['forecastStart'].strftime("%H"))
      for days in range(7):
        with tag('tr'):
          doc.attr(style=f"background-image: url('/theme/images/{locationData.locations[locationName]['locationcode']}_bg.png'")
          with tag('td'):
            doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
            forecastHourly = weatherData['forecastHourly']['hours'][days * 24]
            text(f"{forecastHourly['forecastStart'].strftime("%a")}")
          for hours in range(24):
            with tag('td'):
              doc.attr(style="padding: 0px")
              forecastHourly = weatherData['forecastHourly']['hours'][days*24 + hours]
              title = forecastHourly['conditionCode']+" Cover: "+str(int(forecastHourly['cloudCover']*100))+"% Visibility: "+str(int(forecastHourly['visibility']/1000))+"km"
              if forecastHourly['daylight']:
                fileName = f"/theme/icons/{forecastHourly['conditionCode'].lower()}-day.svg"
              else:
                fileName = f"/theme/icons/{forecastHourly['conditionCode'].lower()}-night.svg"
              with tag('img'):
                doc.attr(src=f"{fileName}", alt=forecastHourly['conditionCode'], width="40px", height="40px")
                doc.attr(('title', f"{title}"))

  doc.asis(f"<!-- end include wetter-{locationData.locations[locationName]['locationcode']}.include -->")
  index = Path(f"wetter-{locationData.locations[locationName]['locationcode']}.include")
  index.write_text(doc.getvalue())

  shutil.copy(index, Path(f"{rootserver['basedir']}/pages/"))
  shutil.copy(locationData.locations[locationName]['locationcode'] + "_bg.png", Path(f"/{rootserver['basedir']}/theme/images/"))
  subprocess.run([f"{rootserver['gitdir']}/Server/patchhtml.py"])


if __name__ == '__main__':
  generateData('Gantrisch')
  generateData('Starfront Observatory')
  generateData('Prairie Skies Astro Ranch')
