#!/usr/bin/env python3
from PIL import Image
from PIL import ImageDraw
import json

from Client import phd2Data


def plotCalibration(calibration):
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

    width, height = 480,480
    centerX = width // 2
    centerY = height // 2
    factor = width // 2 / maxCircles
    im = Image.new('RGB', (width, height))
    imdraw = ImageDraw.Draw(im)
    imdraw.line([(centerX, 0), (centerX , height)],fill ="white", width = 1)
    imdraw.line([(0,centerY), (width,centerY)],fill ="white", width = 1)
    for radius in range(maxCircles):
      imdraw.ellipse((centerX-radius*factor, centerY-radius*factor, centerX+radius*factor, centerY+radius*factor),outline ="lightgrey")
    im.show()


def genDiv():
  phd2Data = json.load(open('../Temp/phdStatus.json'))
  plotCalibration(phd2Data['calibration'])
  pass

genDiv()













genDiv()