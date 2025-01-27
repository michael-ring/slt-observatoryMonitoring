#!/usr/bin/env python3
import sys
from pathlib import Path
import re
import itertools
from fits2image import conversions
from astropy.io import fits

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


def findMostRecentFitsFiles(count=200):
  fileset = dict()
  returnset=[]
  basedir = Path(telescope['imagebasedir'])
  logger.info(f"Searching for fits files in {telescope['imagebasedir']}")
  files = basedir.glob("????-??-??/**/*.fits")
  for file in files:
    fileDateRegex = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    results = fileDateRegex.findall(file.name)
    if len(results) != 1:
      print(f"Either date/time pattern not found in {file.name} or too many hits")
      logger.error(f"Either date/time pattern not found in {file.name} or too many hits")
      raise Exception(f"Either date/time pattern not found in {file.name}")
    if not file.name.startswith('Calibration_'):
      fileset[results[0]] = {'FileName': file}
  fileset = dict(sorted(fileset.items(), reverse=True))
  fileset = dict(itertools.islice(fileset.items(), count))
  for value in fileset.values():
    returnset.append(value)
  logger.info(f'Found {len(returnset)} fits files')
  return returnset


def extractFitsHeaders(fitsFile):
  fitsFile = Path(fitsFile)
  header = fits.getheader(fitsFile)
  return header

def convertFitsToJPG(fitsFile, jpgFile):
  conversions.fits_to_jpg(fitsFile, jpgFile, width=2000, height=2000)


def convertFitsToJPGThumb(fitsFile, jpgFile):
  conversions.fits_to_jpg(fitsFile, jpgFile, width=256, height=256)


if __name__ == '__main__':
  a=findMostRecentFitsFiles()
  pass
