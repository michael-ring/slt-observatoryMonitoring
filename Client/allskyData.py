#!/usr/bin/env python3
import datetime
import sys
from pathlib import Path

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def findMostRecentAllSkyFile():
  fileset=dict()
  basedir = Path(telescope['allskybasedir'])
  today=datetime.date.today().strftime("%m-%d-%Y")
  files=basedir.glob(f"{today}/*.jpg")
  ctime=0
  latestFile=None
  for file in files:
    if file.stat().st_ctime > ctime:
      ctime=file.stat().st_ctime
      latestFile=file
  return latestFile

def findMostRecentAllSkyFiles():
  basedir = Path(telescope['allskybasedir'])
  today=datetime.date.today().strftime("%m-%d-%Y")
  if "testing" in telescope and telescope['testing'] == True:
    today="07-29-2024"
  files = list(basedir.glob(f"{today}/*.jpg"))
  yesterday=(datetime.date.today()-datetime.timedelta(days=1)).strftime("%m-%d-%Y")
  if "testing" in telescope and telescope['testing'] == True:
    yesterday="07-28-2024"
  files += list(basedir.glob(f"{yesterday}/*.jpg"))
  return files

def generateJson():
  result={}
  result['allSky']=[]
  files = findMostRecentAllSkyFiles()
  for file in files:
    result['allSky'].append(file.name)
  return result

findMostRecentAllSkyFiles()