#!/usr/bin/env python3
import sys
from pathlib import Path
import jsonLogHelper

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


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
  else:
    logger.error(f"RoofStatus file {Path(telescope['roofstatusdir']) / 'RoofStatusFile.txt'} not found")
  logger.info("RoofStatus: " + roofStatus)
  return roofStatus


if __name__ == '__main__':
  generateJson()
