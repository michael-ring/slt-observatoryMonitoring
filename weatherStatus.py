#!/usr/bin/env python
import locationData
from yattag import Doc
from pathlib import Path
from fabric import Connection
from PIL import Image
import platform
import shutil
import subprocess

def runningOnServer():
  return platform.uname().node == '91-143-83-61'

def generateData(locationName):
  location = locationData.locations[locationName]
  weatherData = locationData.getWeatherdata(location)
  sunData = locationData.getSunData(location)

  width, height = 960, 40
  im = Image.new('RGB', (width+40, height))
  ld = im.load()

  for x in range(width):
    if x < int((sunData['set'].hour/24+sunData['set'].minute/24/60)*width+width/2) % width:
      r, g, b = 128,128,255
    elif x < int((sunData['twilightset'].hour*1/24+sunData['twilightset'].minute*1/24/60)*width+width/2) % width:
      r, g, b =  96, 96,255
    elif x < int((sunData['nauticalset'].hour*1/24+sunData['nauticalset'].minute*1/24/60)*width+width/2) % width:
      r, g, b =  48, 48,128
    elif x < int((sunData['astronomicalset'].hour * 1 / 24 + sunData['astronomicalset'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b =   0,  0,128
    elif x < int((sunData['astronomicalrise'].hour * 1 / 24 + sunData['astronomicalrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b =   0,  0,  0
    elif x < int((sunData['nauticalrise'].hour * 1 / 24 + sunData['nauticalrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b =   0,  0,128
    elif x < int((sunData['twilightrise'].hour * 1 / 24 + sunData['twilightrise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b =  40, 48,128
    elif x < int((sunData['rise'].hour * 1 / 24 + sunData['rise'].minute * 1 / 24 / 60) * width + width / 2) % width:
      r, g, b =  96, 96,255
    else:
      r, g, b = 128,128,255

    for y in range(height):
      ld[x+40, y] = r, g, b
  for x in range(40):
    for y in range(40):
      ld[x, y] = 128,128,255

  im.save(locationData.locations[locationName]['locationcode']+'_bg.png')

  doc, tag, text = Doc().tagtext()
  doc.asis(f'<!-- begin include wetter-{locationData.locations[locationName]['locationcode']}.include -->')
  with tag('section'):
    doc.attr(id="content", klass="body")

  with tag('section'):
    doc.attr( id="content", klass="body" )
    with tag('h2'):
      text('Darkness Info')
    with tag('table'):
      with tag('tr'):
        for title in 'Sunset', 'Twilight', 'Nautical Dark', 'Astronomical Dark','Astronomical Dark', 'Nautical Dark','Twilight','Sunrise':
          with tag('th'):
            text(title)
      with tag('tr'):
        for data in 'set','twilightset','nauticalset','astronomicalset','astronomicalrise','nauticalrise','twilightrise','rise' :
          with tag('td'):
            text(sunData[data].strftime("%H:%M"))
  with tag('section'):
    doc.attr( id="content", klass="body" )
    with tag('h2'):
      text('Current Weather')
    with tag('table'):
      with tag('tr'):
        for title in 'Local Time','Cloud Cover','High Clouds','Mid Clouds','Low Clouds','Temperature','Dew Point','Wind Speed','Wind Gust':
          with tag('th'):
            text(title)
      with tag('tr'):
        with tag('td'):
          text(weatherData["currentWeather"]["asOf"].strftime("%H:%M"))
        with tag('td'):
          text(f"{int(weatherData["currentWeather"]["cloudCover"]*100)}%")
        with tag('td'):
          text(f"{int(weatherData["currentWeather"]["cloudCoverHighAltPct"]*100)}%")
        with tag('td'):
          text(f"{int(weatherData["currentWeather"]["cloudCoverMidAltPct"] * 100)}%")
        with tag('td'):
          text(f"{int(weatherData["currentWeather"]["cloudCoverLowAltPct"] * 100)}%")
        with tag('td'):
          text(f"{round(weatherData["currentWeather"]["temperature"])}°C")
        with tag('td'):
          text(f"{round(weatherData["currentWeather"]["temperatureDewPoint"])}°C")
        with tag('td'):
          text(f"{round(weatherData["currentWeather"]["windSpeed"])}km/h")
        with tag('td'):
          text(f"{round(weatherData["currentWeather"]["windGust"])}km/h")

  with tag('section'):
    doc.attr( id="content", klass="body" )
    with tag('h2'):
      text('Hourly Forecast')
    with tag('table'):
      doc.attr(width="1000px")
      with tag('tr'):
        with tag('th'):
          doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
          text("")
        for hours in range(24):
          forecastHourly = weatherData["forecastHourly"]["hours"][0 + hours]
          with tag('th'):
            doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
            text(forecastHourly["forecastStart"].strftime('%H'))
      for days in range(7):
        with tag('tr'):
          doc.attr(style=f"background-image: url('/theme/images/{locationData.locations[locationName]['locationcode']}_bg.png'")
          with tag('td'):
            doc.attr(style="width: 40px; padding: 0px; vertical-align: middle; text-align: center")
            forecastHourly = weatherData["forecastHourly"]["hours"][days * 24]
            text(f"{forecastHourly["forecastStart"].strftime('%a')}")
          for hours in range(24):
            with tag('td'):
              doc.attr(style="padding: 0px")
              forecastHourly = weatherData["forecastHourly"]["hours"][days*24 + hours]
              title = forecastHourly["conditionCode"]+" Cover: "+str(int(forecastHourly["cloudCover"]*100))+"% Visibility: "+str(int(forecastHourly["visibility"]/1000))+"km"
              if forecastHourly["daylight"] == True:
                fileName = f'/theme/icons/{forecastHourly["conditionCode"].lower()}-day.svg'
              else:
                fileName = f'/theme/icons/{forecastHourly["conditionCode"].lower()}-night.svg'
              with tag('img'):
                doc.attr(src=f"{fileName}", alt=forecastHourly["conditionCode"], width="40px", height="40px")
                doc.attr(('title',f"{title}"))

  doc.asis(f'<!-- end include wetter-{locationData.locations[locationName]['locationcode']}.include -->')
  index=Path(f"wetter-{locationData.locations[locationName]['locationcode']}.include")
  index.write_text(doc.getvalue())

  if runningOnServer() == False:
    result = Connection('temp.michael-ring.org',user="root",connect_kwargs={ "key_filename": "/Users/tgdrimi9/.ssh/id_rsa",} ).put(f'wetter-{locationData.locations[locationName]['locationcode']}.include', remote=f'/var/www/html/slt-observatory.space/pages/')
    print("Uploaded {0.local} to {0.remote}".format(result))
    result = Connection('temp.michael-ring.org',user="root",connect_kwargs={ "key_filename": "/Users/tgdrimi9/.ssh/id_rsa",} ).put(locationData.locations[locationName]['locationcode']+'_bg.png', remote='/var/www/html/slt-observatory.space/theme/images/')
    print("Uploaded {0.local} to {0.remote}".format(result))
    result = Connection('temp.michael-ring.org', user="root",connect_kwargs={"key_filename": "/Users/tgdrimi9/.ssh/id_rsa", }).run('/root/devel/slt-observatoryMonitoring/patchhtml.py')
    print(result)
  else:
    shutil.copy(index,Path("/var/www/html/slt-observatory.space/pages/"))
    shutil.copy(locationData.locations[locationName]['locationcode']+'_bg.png', Path("/var/www/html/slt-observatory.space/theme/images/"))
    subprocess.run(["/root/devel/slt-observatoryMonitoring/patchhtml.py"])
generateData('Gantrisch')
generateData('Starfront Observatory')
generateData('Prairie Skies Astro Ranch')
