#!/usr/bin/env python3
from PIL import Image
from PIL import ImageDraw
import sys
import json
from pathlib import Path

sys.path.append('.')
sys.path.append('..')
from Common.config import rootserver,runningOnServer,logger


def plotCalibration(calibration):
  logger.info("Plotting Calibration Data for phd2")
  Direction = 0
  dx = 2
  dy = 3
  Dist = 6
  maxXY = 0.0
  for calibrationTime in calibration:
    for step in calibration[calibrationTime]['steps']:
      step = step.split(',')
      x = abs(float(step[dx]))
      y = abs(float(step[dy]))
      if x > maxXY:
        maxXY = x
      if y > maxXY:
        maxXY = y
    maxCircles = int(maxXY) // 5 + 1

    width, height = 480, 480
    centerX = width // 2
    centerY = height // 2
    factor = width // 2 / maxCircles
    im = Image.new('RGB', (width, height))
    imdraw = ImageDraw.Draw(im)
    imdraw.line([(centerX, 0), (centerX, height)], fill="white", width=1)
    imdraw.line([(0, centerY), (width, centerY)], fill="white", width=1)
    for radius in range(maxCircles):
      imdraw.ellipse((centerX-radius*factor, centerY-radius*factor, centerX+radius*factor, centerY+radius*factor), outline="lightgrey")
    im.show()


def genDiv(telescopeName):
  if runningOnServer():
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/phd2Status.json')) as f:
      phd2Data = json.load(f)
  else:
    with open(Path(__file__).parent.parent / f'Test/{telescopeName}-data/phd2Status.json') as f:
      phd2Data = json.load(f)

  if phd2Data == []:
    return ""
  plotCalibration(phd2Data['calibration'])
  pass


if __name__ == '__main__':
  genDiv('slt')
