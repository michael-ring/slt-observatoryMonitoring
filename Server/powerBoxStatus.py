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
  from config import locations,telescopes,rootserver
except:
  print("locations configuration is missing in config.py")
  sys.exit(1)

def runningOnServer():
  return platform.uname().node == rootserver['nodename']

def genDiv(telescopeName):
  width, height = 1024, 200
  telescope=telescopes[telescopeName]
  localtz=locations[telescope['location']]['timezone']

  if runningOnServer() == True:
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/powerboxStatus.json')) as f:
      powerBoxData=json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/powerboxStatus.json') as f:
      powerBoxData=json.load(f)

  start_time=datetime.now(ZoneInfo(localtz))
  if start_time.hour < 12:
    start_time = start_time.replace(hour=0,minute=0,second=0,microsecond=0) - timedelta(hours=12)
  else:
    start_time = start_time.replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(hours=12)

  timestamps=[]
  temperatures=[]
  dewpoints=[]
  probe1temperatures=[]
  probe2temperatures=[]
  #probe3temperatures=[]

  for dataset in powerBoxData:
    timestamp = next(iter(dataset.keys()))
    timestamps.append(parser.parse(timestamp).replace(tzinfo=ZoneInfo(localtz)))
    temperatures.append(float(dataset[timestamp]['temperature']))
    dewpoints.append(float(dataset[timestamp]['dewpoint']))
    if dataset[timestamp]['probe1temperature'] != "-127.00":
      probe1temperatures.append(float(dataset[timestamp]['probe1temperature']))
    if dataset[timestamp]['probe2temperature'] != "-127.00":
      probe2temperatures.append(float(dataset[timestamp]['probe2temperature']))
    #probe3temperatures.append(float(dataset[timestamp]['probe3temperature']))
  #minutes = mdates.drange(start_time, start_time + timedelta(days=1), timedelta(minutes=10))
  px = 1 / plt.rcParams['figure.dpi']
  plt.subplots(figsize=(width * px, height * px))

  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=tz.gettz(localtz)))
  plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 3))
  #plt.ylim(-10, 40)
  plt.xlim(start_time,start_time+timedelta(days=1))
  plt.grid(True)
  plt.ylabel("°C")
  plt.plot(timestamps, temperatures, label='Temperature')
  plt.plot(timestamps, dewpoints, label='Dewpoint')
  if len(probe1temperatures) > 0:
    plt.plot(timestamps, probe1temperatures, label='Scope Temperature')
  if len(probe2temperatures) > 0:
    plt.plot(timestamps, probe2temperatures, label='GuideScope Temperature')
  plt.gcf().autofmt_xdate()
  plt.legend()
  if runningOnServer() == True:
    plt.savefig(Path(rootserver['basedir'] / 'images' / 'powerBoxStatus.png'))
  else:
    plt.savefig(Path(__file__).parent.parent / f'Test/images/{telescopeName}-powerBoxStatus.png')

  latestPowerBoxData=list(powerBoxData[-1].values())[-1]
  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr( id='content', klass='body' )
    with tag('h2'):
      text("PowerBox Info")
    with tag('table'):
      with tag('tr'):
        for title in 'Port3/4 Voltage','Port3/4 Current','InputVoltage','InputCurrent','Port5 PWM','Port6 PWM','Port7 PWM','Firmware Version':
          with tag('th'):
            text(title)
      with tag('tr'):
        with tag('td'):
          text(f"{latestPowerBoxData['dc34voltage']:.2f} V")
        with tag('td'):
          text(f"{float(latestPowerBoxData['adjustableoutputcurrent']):.2f} A")
        with tag('td'):
          text(f"{float(latestPowerBoxData['inputvoltage']):.2f} V")
        with tag('td'):
          text(f"{float(latestPowerBoxData['inputcurrent']):.2f} A")
        with tag('td'):
          text(latestPowerBoxData['dc5status'])
        with tag('td'):
          text(latestPowerBoxData['dc6status'])
        with tag('td'):
          text(latestPowerBoxData['dc7status'])
        with tag('td'):
          text(latestPowerBoxData['firmwareversion'])

    with tag('h3'):
      text("Temperature/Dewpoint measured at Telescope")
    with tag('img'):
      doc.attr( src=f'images/{telescopeName}-powerBoxStatus.png', alt=f'{telescopeName}-powerBoxStatus.png' )

  if runningOnServer() == True:
    with open(Path(f'{rootserver['basedir']}/{telescopeName}-powerBoxStatus.include'),mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/{telescopeName}-powerBoxStatus.html',mode='w') as f:
      f.writelines(doc.getvalue())

if __name__ == '__main__':
  genDiv('vst')
