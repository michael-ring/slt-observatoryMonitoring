#!/usr/bin/env python3
import json
import platform
from yattag import Doc
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from datetime import datetime
from datetime import timedelta
from dateutil import tz
from dateutil import parser
from zoneinfo import ZoneInfo

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import locations, telescopes, rootserver
except:
  print("locations configuration is missing in config.py")
  sys.exit(1)


def runningOnServer():
  return platform.uname().node == rootserver['nodename']


def genDiv(telescopeName):
  width, height = 1024, 200
  telescope = telescopes[telescopeName]
  localtz = locations[telescope['location']]['timezone']

  if runningOnServer():
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/weatherStatus.json')) as f:
      skyAlertData = json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/weatherStatus.json') as f:
      skyAlertData = json.load(f)

  start_time = datetime.now(tz=tz.gettz('UTC')).astimezone(tz.gettz(localtz))

  if start_time.hour < 12:
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=12)
  else:
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=12)

  timestamps = []
  temperatures = []
  dewpoints = []
  windspeeds = []

  for dataset in skyAlertData:
    timestamp = next(iter(dataset.keys()))
    if dataset[timestamp] != {}:
      timestamps.append(parser.parse(timestamp).astimezone(tz.gettz(localtz)))
      temperatures.append(float(dataset[timestamp]['ambienttemp']))
      dewpoints.append(float(dataset[timestamp]['dewpoint']))
      windspeeds.append(float(dataset[timestamp]['windspeed']))
  px = 1 / plt.rcParams['figure.dpi']
  plt.subplots(figsize=(width * px, height * px))

  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz.gettz(localtz)))
  plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
  #plt.ylim(-10, 40)
  plt.xlim(start_time, start_time+timedelta(days=1))
  plt.grid(True)
  plt.ylabel("°C")
  plt.plot(timestamps, temperatures, label='Temperature')
  plt.plot(timestamps, dewpoints, label='Dewpoint')
  plt.gcf().autofmt_xdate()
  plt.legend()
  if runningOnServer():
    plt.savefig(Path(rootserver['basedir']) / 'images' / 'skyAlertStatus.png')
  else:
    plt.savefig(Path(__file__).parent.parent / f'Test/images/{telescopeName}-skyAlertStatus.png')

  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("SkyAlert Info")
    with tag('h3'):
      text("Temperature/Dewpoint measured on site")
    with tag('img'):
      if runningOnServer():
        doc.attr(src=f'https://{rootserver['name']}/images/{telescopeName}-skyAlertStatus.png', alt=f'{telescopeName}-skyAlertStatus.png')
      else:
        doc.attr(src=f'/images/{telescopeName}-skyAlertStatus.png', alt=f'{telescopeName}-skyAlertStatus.png')

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/pages/status-{telescopeName}.skyAlertStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.skyAlertStatus.include', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()


if __name__ == '__main__':
  genDiv('vst')
