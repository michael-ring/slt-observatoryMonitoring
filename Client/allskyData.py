#!/usr/bin/env python3
import os
from datetime import datetime,date,timedelta
import sys
from pathlib import Path

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


def findMostRecentAllSkyFile():
  basedir = Path(telescope['allskybasedir'])
  today = date.today().strftime("%m-%d-%Y")
  logger.info(f"Searching for AllSky Files in: {basedir / today}")
  files = basedir.glob(f"{today}/*.jpg")
  ctime = 0
  latestFile = None
  for file in files:
    if file.stat().st_ctime > ctime:
      ctime = file.stat().st_ctime
      latestFile = file
  if latestFile is None:
    logger.error(f"No AllSky files found in {basedir / today}")
  else:
    logger.info(f"Found {latestFile}")
  return latestFile


def findAllSkyFiles(requiredDates=None):
  files = []
  basedir = Path(telescope['allskybasedir'])
  if requiredDates is None  or requiredDates == []:
    today = date.today().strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] is True:
      today = "07-29-2024"
    logger.info(f"Searching for AllSky Files in: {basedir / today}")
    files = list(basedir.glob(f"{today}/*.jpg"))
    logger.info(f"Searching for AllSky Files in: {basedir / today}")
    yesterday = (date.today()-timedelta(days=1)).strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] is True:
      yesterday = "07-28-2024"
    logger.info(f"Searching for AllSky Files in: {basedir / yesterday}")
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
      logger.info(f"Searching for AllSky Files in: {basedir / requiredDate}")
      files = files + list(basedir.glob(f"{requiredDate}/*.jpg"))
  lastTimestamp = datetime.fromtimestamp(0)
  result = []
  if files == []:
    logger.error(f"No AllSky files found")
    return []

  files.sort(key=os.path.getctime)
  for file in files:
    timestamp=datetime.fromtimestamp(file.stat().st_ctime)
    if (timestamp - lastTimestamp).total_seconds() >=600.0:
      lastTimestamp = timestamp
      result.append(file)
  logger.info(f"Found {len(result)} AllSky Files")
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