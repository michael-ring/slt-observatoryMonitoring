#!/usr/bin/env python3
import os
from datetime import datetime,date,timedelta
import sys
from pathlib import Path

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def findMostRecentAllSkyFile():
  basedir = Path(telescope['allskybasedir'])
  today = date.today().strftime("%m-%d-%Y")
  files = basedir.glob(f"{today}/*.jpg")
  ctime = 0
  latestFile = None
  for file in files:
    if file.stat().st_ctime > ctime:
      ctime = file.stat().st_ctime
      latestFile = file
  return latestFile


def findAllSkyFiles(requiredDates=None):
  files = []
  basedir = Path(telescope['allskybasedir'])
  if requiredDates is None:
    today = date.today().strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] is True:
      today = "07-29-2024"
    files = list(basedir.glob(f"{today}/*.jpg"))
    yesterday = (date.today()-timedelta(days=1)).strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] is True:
      yesterday = "07-28-2024"
    files += list(basedir.glob(f"{yesterday}/*.jpg"))
  else:
    for index, value in enumerate(requiredDates):
      requiredDates[index] = value[5:7] + '-' + value[8:10] + '-' + value[0:4]
    today = date.today().strftime("%m-%d-%Y")
    if today not in requiredDates:
      requiredDates.append(today)
    yesterday = (date.today()-timedelta(days=1)).strftime("%m-%d-%Y")
    if yesterday not in requiredDates:
      requiredDates.append(yesterday)
    for requiredDate in requiredDates:
      files = files + list(basedir.glob(f"{requiredDate}/*.jpg"))
  lastTimestamp = datetime.fromtimestamp(0)
  result = []
  files.sort(key=os.path.getctime)
  for file in files:
    timestamp=datetime.fromtimestamp(file.stat().st_ctime)
    if (timestamp - lastTimestamp).total_seconds() >=600.0:
      lastTimestamp = timestamp
      result.append(file)
  return result


def generateJson(requiredDates=None):
  result = dict()
  result['allSky'] = []
  files = findAllSkyFiles(requiredDates)
  for file in files:
    result['allSky'].append(file.name)
  return result


if __name__ == '__main__':
  generateJson()