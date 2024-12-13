from pathlib import Path
from datetime import datetime, timedelta
import json


def getDailyLog(basename):
  minus12h = (datetime.now() - timedelta(hours=12, minutes=0)).strftime('%Y-%m-%d')
  jsonFile = Path(__file__).parent.parent / 'Temp' / f"{basename}_{minus12h}.json"
  if jsonFile.exists():
    with open(jsonFile, 'r') as f:
      _json = json.load(f)
  else:
    _json = []
  return _json


def writeDailyLog(basename, _json):
  minus12h = (datetime.now() - timedelta(hours=12, minutes=0)).strftime('%Y-%m-%d')
  jsonFile = Path(__file__).parent.parent / 'Temp' / f"{basename}_{minus12h}.json"
  with open(jsonFile, 'w') as f:
    json.dump(_json, f, indent=0)


def appendToDailyLog(filename, _json):
  _json2 = {}
  index = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  _json2[index] = _json
  alljson = getDailyLog(filename)
  alljson.append(_json2)
  writeDailyLog(filename, alljson)
  return alljson
