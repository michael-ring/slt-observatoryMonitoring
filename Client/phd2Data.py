import sys
import datetime
from pathlib import Path

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def generateJson(requiredDates=None):
  if 'phdlogbasedir' in telescope:
    basedir = Path(telescope['phdlogbasedir'])
    files=[]
    if requiredDates is None  or requiredDates == []:
      today = datetime.date.today().strftime("%Y-%m-%d")
      if "testing" in telescope and telescope['testing'] is True:
        today = "2024-08-29"
      files = list(basedir.glob(f"PHD2_GuideLog_{today}*.txt"))
      yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
      if "testing" in telescope and telescope['testing'] is True:
        yesterday = "2024-08-27"
      files += list(basedir.glob(f"PHD2_GuideLog_{yesterday}*.txt"))
    else:
      for requiredDate in requiredDates:
        files = files + list(basedir.glob(f"PHD2_GuideLog_{requiredDate}*.txt"))
    if files == []:
      return {}
    files.sort(reverse=False)
    calibration = {}
    guiding = {}
    for filename in files:
      with open(filename) as file:
        inCalibration = False
        inGuiding = False
        while line := file.readline():
          line = line.rstrip()
          if line.startswith("Calibration Begins at "):
            calibrationStart = line[len("Calibration Begins at "):]
            inCalibration = True
            calibration[calibrationStart] = {'steps': []}
            continue
          if line.startswith("Guiding Begins at "):
            guidingStart = line[len("Guiding Begins at "):]
            inGuiding = True
            settling = 0
            dithering = 0
            guiding[guidingStart] = {'steps': []}
            continue

          if inCalibration:
            if line.startswith("Calibration complete"):
              inCalibration = False
              continue
            if line.startswith("West") or line.startswith("East") or line.startswith("South") or line.startswith("North"):
              if line.find('calibration complete') >= 0:
                finishedCal = line.split(' ')[0]
                angle = line.split(' ')[5]
                rate = line.split(' ')[9]
                calibration[calibrationStart][finishedCal] = {'angle': angle, 'rate': rate}
                continue

              calibration[calibrationStart]['steps'].append(line)

          if inGuiding:
            if line.startswith("Guiding Ends at"):
              inGuiding = False
              continue
            if line.startswith("INFO: DITHER"):
              dithering = 1
              continue
            if line.startswith("INFO: SETTLING STATE CHANGE, Settling started"):
              settling = 1
              continue
            if line.startswith("INFO: SETTLING STATE CHANGE, Settling complete"):
              settling = 0
              dithering = 0
              continue
            if line.startswith("SETTLING STATE CHANGE, Settling failed"):
              settling = 0
              dithering = 0
              continue
            if len(line) > 0 and line[0] >= '0' and line[0] <= '9':
              guiding[guidingStart]['steps'].append((line+f",{settling},{dithering}").replace('"', ''))

    return {'calibration': calibration, 'guiding': guiding}


if __name__ == '__main__':
  generateJson()
