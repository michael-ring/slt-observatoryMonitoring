#!/usr/bin/env python3
import datetime
import sys
from pathlib import Path

try:
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
