#!/usr/bin/env python3
import sys
import datetime
from pathlib import Path

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


def generateJson(requiredDates=None):
  if 'ninalogbasedir' in telescope:
    basedir = Path(telescope['ninalogbasedir'])
    files=[]
    if requiredDates is None or requiredDates == []:
      today = datetime.date.today().strftime("%Y%m%d")
      if "testing" in telescope and telescope['testing'] is True:
        today = "20241211"
      logger.info(f"searching for Nina Logfiles {basedir}/{today}*.log")
      files = list(basedir.glob(f"{today}*.log"))
      yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
      if "testing" in telescope and telescope['testing'] is True:
        yesterday = "20241210"
      logger.info(f"searching for Nina Logfiles {basedir}/{yesterday}*.log")
      files += list(basedir.glob(f"{yesterday}*.log"))
    else:
      for requiredDate in requiredDates:
        requiredDate=requiredDate.replace("-","")
        logger.info(f"searching for Nina Logfiles {basedir}/{requireddate}*.log")
        files = files + list(basedir.glob(f"{requiredDate}*.log"))
      today = requiredDates[0].replace("-","")
      yesterday = requiredDates[1].replace("-", "")
    if files == []:
      logger.error("No Nina Log files found")
      return {}
    files.sort(reverse=False)
    ninaData={}
    starttime = datetime.datetime.strptime(yesterday + '120000', '%Y%m%d%H%M%S')
    for file in files:
      lines=open(file).readlines()
      for lineno,line in enumerate(lines):
        if line.find('|') > 0:
          if line.find('|INFO|') > 0:
            infoline=line.split('|')
            if len(infoline) > 5:
              timestamp = datetime.datetime.strptime(infoline[0], '%Y-%m-%dT%H:%M:%S.%f')
              if timestamp > starttime:
                ninaData[timestamp.strftime('%Y-%m-%d %H:%M:%S')] = {'Level': 'INFO', 'Source': infoline[2],
                                                                       'Member': infoline[3],
                                                                       'Line': infoline[4],
                                                                       'Message': infoline[5].replace('\n', '')}
          elif line.find('|ERROR|') > 0:
            errorline=line.split('|')
            if len(errorline) > 5:
              timestamp=datetime.datetime.strptime(errorline[0],'%Y-%m-%dT%H:%M:%S.%f')
              if timestamp > starttime:
                ninaData[timestamp.strftime('%Y-%m-%d %H:%M:%S')] = {'Level':'ERROR','Source':errorline[2],
                                                                     'Member':errorline[3],
                                                                     'Line': infoline[4],
                                                                     'Message':errorline[5].replace('\n','')}

    logger.info(f"Found {len(ninaData)} Nina Log file entries")
    return ninaData

if __name__ == '__main__':
  a = generateJson()
  pass
