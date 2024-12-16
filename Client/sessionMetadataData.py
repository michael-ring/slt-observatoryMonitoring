#!/usr/bin/env python3
import sys
import json
from Client import imageData
from pathlib import Path
import hashlib
import re

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

activeIntKeys = ('DetectedStars', 'Gain')
activeTextKeys = ('acquireddate', 'ExposureDuration', 'FilterName', 'Binning', 'Eccentricity', 'HFR', 'FWHM',
                  'GuidingRMSArcSec', 'GuidingRMSRAArcSec', 'GuidingRMSDECArcSec')


def addMetaData(data):
  metadataRecords = dict()
  for fileinfo in data:
    metaDataPath = Path(fileinfo['FileName']).parent
    metaDataFilePath = None
    while metaDataFilePath is None:
      if (metaDataPath / "ImageMetaData.json").exists():
        metaDataFilePath = metaDataPath / "ImageMetaData.json"
        break
      for metafile in metaDataPath.glob("ImageMetaData*.json"):
        metaDataFilePath = metafile
        break
      metaDataPath = metaDataPath.parent

      if metaDataPath == Path('/') or (metaDataPath == Path('c:/')):
        break
    if metaDataFilePath is None:
      print(f"MetaData file not found based on {Path(data[fileinfo]['FileName']).parent}")
      sys.exit(1)
    metaDataFilePathHash = hashlib.md5(str(metaDataFilePath).encode()).hexdigest()
    if metaDataFilePathHash not in metadataRecords:
      metadataRecords[metaDataFilePathHash] = json.load(metaDataFilePath.open(encoding="utf-8"))
    found = False
    for metadataRecord in metadataRecords[metaDataFilePathHash]:
      if Path(metadataRecord['FilePath']).name == Path(fileinfo['FileName']).name:
        for key in metadataRecord.keys():
          found = True
          newkey = key
          if key == "ExposureStart":
            newkey = "ExposureStartTime"
          if key == "Duration":
            newkey = "ExposureDuration"
          fileinfo[newkey] = metadataRecord[key]
          if isinstance(fileinfo[newkey], float):
            fileinfo[newkey] = f"{fileinfo[newkey]:.2f}"
    if not found:
      for key in activeTextKeys:
        fileinfo[key] = ""
      for key in activeIntKeys:
        fileinfo[key] = 0
    fileDateRegex = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    results = fileDateRegex.findall(Path(metadataRecord['FilePath']).name)
    if len(results) == 1:
      fileinfo['acquireddate'] = results[0][0:10]+' '+results[0][11:13]+':'+results[0][14:16]+':'+results[0][17:19]


def targetStatus():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  return data


def generateJson():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  for item in data:
    item['FileName'] = str(item['FileName'])
  return data


if __name__ == '__main__':
  generateJson()
