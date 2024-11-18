#!/usr/bin/env python3
import sys
import json
from Client import imageData
from pathlib import Path
import hashlib

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

activeIntKeys = ('DetectedStars', 'Gain')
activeTextKeys= ('acquireddate','ExposureDuration','FilterName','Binning','Eccentricity','HFR','FWHM','GuidingRMSArcSec','GuidingRMSRAArcSec','GuidingRMSDECArcSec')

def addMetaData(data,fullDataSet=False):
  metadataRecords={}
  for fileinfo in data:
    metaDataPath=Path(data[fileinfo]['FileName']).parent
    metaDataFilePath=None
    while metaDataFilePath is None:
      p = metaDataPath / "ImageMetaData.json"
      if (metaDataPath / "ImageMetaData.json").exists():
        metaDataFilePath=metaDataPath / "ImageMetaData.json"
        break
      metaDataPath=metaDataPath.parent
      if metaDataPath == Path('/') or (metaDataPath == Path('c:/')):
        break
    if metaDataFilePath == None:
      print(f"MetaData file not found based on {Path(data[fileinfo]['FileName']).parent}")
      sys.exit(1)
    metaDataFilePathHash=hashlib.md5(str(metaDataFilePath).encode()).hexdigest()
    if not metaDataFilePathHash in metadataRecords:
      metadataRecords[metaDataFilePathHash] = json.load(metaDataFilePath.open())
    found=False
    for metadataRecord in metadataRecords[metaDataFilePathHash]:
      if Path(metadataRecord['FilePath']).name == Path(data[fileinfo]['FileName']).name:
        for key in metadataRecord.keys():
          found=True
          newkey=key
          if key == "ExposureStart":
            newkey = "ExposureStartTime"
          if key == "Duration":
            newkey = "ExposureDuration"
          data[fileinfo][newkey] = metadataRecord[key]
          if type(data[fileinfo][newkey]) == float:
            data[fileinfo][newkey] = f"{data[fileinfo][newkey]:.2f}"
    if not found:
      for key in activeTextKeys:
        data[fileinfo][key] = ""
      for key in activeIntKeys:
        data[fileinfo][key] = 0
    data[fileinfo]['acquireddate']=fileinfo[0:10]+' '+fileinfo[11:13]+':'+fileinfo[14:16]+':'+fileinfo[17:19]

def targetStatus():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  return(data)

def generateJson():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data,True)
  for item in data:
    data[item]['FileName'] = str(data[item]['FileName'])
  return(data)

if __name__ == '__main__':
  generateJson()