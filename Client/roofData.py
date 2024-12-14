#!/usr/bin/env python3
import sys
from pathlib import Path
import jsonLogHelper

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def generateJson():
  json = jsonLogHelper.getDailyLog('roofdata')
  _json = dict()
  _json['roof'] = getRoofStatus()
  if json == []:
    result = jsonLogHelper.appendToDailyLog('roofdata', _json)
  else:
    if list(json[-1].values())[-1]['roof'] != _json['roof']:
      result = jsonLogHelper.appendToDailyLog('roofdata', _json)
    else:
      result = jsonLogHelper.getDailyLog('roofdata')
  return result


def getRoofStatus():
  roofStatus = "closed"
  roofDataFile = Path(telescope['roofstatusdir']) / "RoofStatusFile.txt"
  if roofDataFile.exists():
    content = roofDataFile.read_text()
    if content.find("CLOSED") != -1:
      roofStatus = "closed"
    if content.find("OPEN") != -1:
      roofStatus = "open"
  return roofStatus


if __name__ == '__main__':
  generateJson()
