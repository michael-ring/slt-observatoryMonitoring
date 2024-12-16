#!/usr/bin/env python3
import sys
from pathlib import Path
import re
import itertools
from fits2image import conversions

try:
  sys.path.append('..')
  from config import rootserver
except:
  print("rootserver configuration is missing in config.py")
  sys.exit(1)

try:
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def findMostRecentFitsFiles(count=200):
  fileset = dict()
  returnset=[]
  basedir = Path(telescope['imagebasedir'])
  files = basedir.glob("????-??-??/**/*.fits")
  for file in files:
    fileDateRegex = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    results = fileDateRegex.findall(file.name)
    if len(results) != 1:
      print(f"Either date/time pattern not found in {file.name} or too many hits")
      sys.exit(1)
    if not file.name.startswith('Calibration_'):
      fileset[results[0]] = {'FileName': file}
  fileset = dict(sorted(fileset.items(), reverse=True))
  fileset = dict(itertools.islice(fileset.items(), count))
  for value in fileset.values():
    returnset.append(value)
  return returnset


def convertFitsToJPG(fitsFile, jpgFile):
  conversions.fits_to_jpg(fitsFile, jpgFile, width=2000, height=2000)


def convertFitsToJPGThumb(fitsFile, jpgFile):
  conversions.fits_to_jpg(fitsFile, jpgFile, width=256, height=256)


if __name__ == '__main__':
  findMostRecentFitsFiles()
