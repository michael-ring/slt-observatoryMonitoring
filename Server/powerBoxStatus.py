#!/usr/bin/env python3
import json
from yattag import Doc
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from datetime import timedelta
from dateutil import tz
from dateutil import parser

sys.path.append('.')
sys.path.append('..')
from Common.config import locations,telescopes,rootserver,runningOnServer,logger


def genDiv(telescopeName):
  width, height = 1024, 200
  telescope = telescopes[telescopeName]
  localtz = locations[telescope['location']]['timezone']

  if runningOnServer() is True:
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/powerboxStatus.json')) as f:
      powerBoxData = json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/powerboxStatus.json') as f:
      powerBoxData = json.load(f)

  start_time = parser.parse(next(iter(powerBoxData[0].keys())))
  if start_time.hour < 12:
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=12)
  else:
    start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=12)

  timestamps = []
  temperatures = []
  dewpoints = []
  probe1temperatures = []
  probe2temperatures = []
  #probe3temperatures = []

  for dataset in powerBoxData:
    timestamp = next(iter(dataset.keys()))
    timestamps.append(parser.parse(timestamp).astimezone(tz.gettz(localtz)))
    try:
      temperatures.append(float(dataset[timestamp]['temperature']))
      dewpoints.append(float(dataset[timestamp]['dewpoint']))
      if dataset[timestamp]['probe1temperature'] != "-127.00":
        probe1temperatures.append(float(dataset[timestamp]['probe1temperature']))
      if dataset[timestamp]['probe2temperature'] != "-127.00":
        probe2temperatures.append(float(dataset[timestamp]['probe2temperature']))
      #probe3temperatures.append(float(dataset[timestamp]['probe3temperature']))
    except:
      logger.exception()

  px = 1 / plt.rcParams['figure.dpi']
  plt.subplots(figsize=(width * px, height * px))

  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
  plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
  plt.xlim(start_time, start_time+timedelta(days=1))
  plt.grid(True)
  plt.ylabel("°C")
  plt.plot(timestamps, temperatures, label='Temperature')
  plt.plot(timestamps, dewpoints, label='Dewpoint')
  if len(probe1temperatures) > 0:
    try:
      plt.plot(timestamps, probe1temperatures, label='Scope Temperature')
    except Exception as e:
      logger.exception('Plot of Scope Temperature failed')
      pass

  if len(probe2temperatures) > 0:
    try:
      plt.plot(timestamps, probe2temperatures, label='GuideScope Temperature')
    except Exception as e:
      logger.exception('Plot of Guidescope Temperature failed')
      pass
  plt.gcf().autofmt_xdate()
  plt.legend()
  if runningOnServer():
    plt.savefig(Path(rootserver['basedir']) / 'images' / f'{telescopeName}-images' / 'powerBoxStatus.png')
  else:
    plt.savefig(Path(__file__).parent.parent / f'Test/images/{telescopeName}-powerBoxStatus.png')

  latestPowerBoxData = list(powerBoxData[-1].values())[-1]
  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("PowerBox Info")
    with tag('table'):
      with tag('tr'):
        for title in 'Port3/4 Voltage', 'Port3/4 Current', 'InputVoltage', 'InputCurrent', 'Port5 PWM', 'Port6 PWM', 'Port7 PWM', 'Firmware Version':
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
      if runningOnServer():
        doc.attr(src=f'https://{rootserver['name']}/images/{telescopeName}-images/powerBoxStatus.png', alt=f'powerBoxStatus.png')
      else:
        doc.attr(src=f'images/{telescopeName}-powerBoxStatus.png', alt=f'{telescopeName}-powerBoxStatus.png')

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/pages/status-{telescopeName}.powerBoxStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.powerBoxStatus.include', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()


if __name__ == '__main__':
  genDiv('vst')
