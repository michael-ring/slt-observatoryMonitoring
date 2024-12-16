#!/usr/bin/env python3
import sys
import datetime
from pathlib import Path


try:
  sys.path.append('.')
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def generateJson(requiredDates=None):
  print(requiredDates)
  ninaErrorsBlacklist = {'DllLoader.cs': ['LoadDllFromAbsolutePath'],
    'ToupTekAlikeCamera.cs': ['TemperatureSetPoint'],
    'AscomDevice.cs': ['GetProperty']
  }
  ninaInfoWhitelist = {'FocuserMediator.cs': ['BroadcastSuccessfulAutoFocusRun'],
    'SequenceTrigger.cs': ['Run'],
    'HocusFocusStarDetection.cs': ['Detect'],
    'FocuserVM.cs':['MoveFocuserInternal'],
    'AutoFocusEngine.cs': ['StartBlindFocusPoints']
  }
  if 'ninalogbasedir' in telescope:
    basedir = Path(telescope['ninalogbasedir'])
    files=[]
    if requiredDates is None:
      today = datetime.date.today().strftime("%Y%m%d")
      if "testing" in telescope and telescope['testing'] is True:
        today = "20241211"
      files = list(basedir.glob(f"{today}*.log"))
      yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
      if "testing" in telescope and telescope['testing'] is True:
        yesterday = "20241210"
      files += list(basedir.glob(f"{yesterday}*.log"))
    else:
      for requiredDate in requiredDates:
        requiredDate=requiredDate.replace("-","")
        files = files + list(basedir.glob(f"{requiredDate}*.log"))
      today = requiredDates[0].replace("-","")
      yesterday = requiredDates[1].replace("-", "")
    if files == []:
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
              if infoline[2] in ninaInfoWhitelist and infoline[3] in ninaInfoWhitelist[infoline[2]]:
                timestamp = datetime.datetime.strptime(infoline[0], '%Y-%m-%dT%H:%M:%S.%f')
                if timestamp > starttime:
                  ninaData[timestamp.strftime('%Y-%m-%d %H:%M:%S')] = {'Level': 'Info', 'Source': infoline[2],
                                                                       'Member': infoline[3],
                                                                       'Message': infoline[5].replace('\n', '')}
          elif line.find('|ERROR|') > 0:
            errorline=line.split('|')
            if len(errorline) > 5:
              if errorline[2] in ninaErrorsBlacklist and errorline[3] in ninaErrorsBlacklist[errorline[2]]:
                pass
              else:
                timestamp=datetime.datetime.strptime(errorline[0],'%Y-%m-%dT%H:%M:%S.%f')
                if timestamp > starttime:
                  ninaData[timestamp.strftime('%Y-%m-%d %H:%M:%S')] = {'Level':'ERROR','Source':errorline[2],'Member':errorline[3],'Message':errorline[5].replace('\n','')}

    return ninaData

if __name__ == '__main__':
  generateJson()