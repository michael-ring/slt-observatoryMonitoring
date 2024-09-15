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

def findAllSkyFiles(requiredDates=None):
  files=[]
  basedir = Path(telescope['allskybasedir'])
  if requiredDates is None:
    today=datetime.date.today().strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] == True:
      today="07-29-2024"
    files = list(basedir.glob(f"{today}/*.jpg"))
    yesterday=(datetime.date.today()-datetime.timedelta(days=1)).strftime("%m-%d-%Y")
    if "testing" in telescope and telescope['testing'] == True:
      yesterday="07-28-2024"
    files += list(basedir.glob(f"{yesterday}/*.jpg"))
  else:
    for index,value in enumerate(requiredDates):
      requiredDates[index]=value[3:4]+'-'+value[0:1]+'-'+value[6:7]
    today=datetime.date.today().strftime("%m-%d-%Y")
    if today not in requiredDates:
      requiredDates.append(today)
    yesterday=(datetime.date.today()-datetime.timedelta(days=1)).strftime("%m-%d-%Y")
    if yesterday not in requiredDates:
      requiredDates.append(yesterday)
    for requiredDate in requiredDates:
      files = files + list(basedir.glob(f"{requiredDate}/*.jpg"))
  return files

def generateJson(requiredDates=None):
  result={}
  result['allSky']=[]
  files = findAllSkyFiles(requiredDates)
  for file in files:
    result['allSky'].append(file.name)
  return result
