#!/usr/bin/env python3
import sys
import json
from Client import imageData
from pathlib import Path
import re

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

activeKeys = 'ExposureStart','Duration','DetectedStars', 'Eccentricity','FilterName','Duration','Binning','Gain','HFR','FWHM','GuidingRMSArcSec','GuidingRMSRAArcSec','GuidingRMSDECArcSec'

def addMetaData(data,fullDataSet=False):
  for fileinfo in data:
    metaDataPath=Path(data[fileinfo]['filename']).parent
    fileDateRegex=re.compile(r"^\d{4}-\d{2}-\d{2}$")
    metaDataFilePath=None
    while metaDataPath.name != "":
      results=fileDateRegex.findall(metaDataPath.name)
      if len(results) == 1:
        metaDataFilePath=metaDataPath / "ImageMetaData.json"
        break
      metaDataPath=metaDataPath.parent
    if metaDataFilePath == None:
      print(f"MetaData file not found based on {Path(data[fileinfo]['filename']).parent}")
      sys.exit(1)
    metadataRecords = json.load(metaDataFilePath.open())
    for metadataRecord in metadataRecords:
      if Path(metadataRecord['FilePath']).name == Path(data[fileinfo]['filename']).name:
        if fullDataSet == False:
          for key in activeKeys:
            if key in metadataRecord.keys():
              data[fileinfo][key] = metadataRecord[key]
              if type(data[fileinfo][key]) == float:
                data[fileinfo][key] = f"{data[fileinfo][key]:.2f}"
            else:
              data[fileinfo][key] = 'None'
              data[fileinfo][key] = metadataRecord[key]
              if type(data[fileinfo][key]) == float:
                data[fileinfo][key] = f"{data[fileinfo][key]:.2f}"
        else:
          for key in metadataRecord.keys():
            data[fileinfo][key] = metadataRecord[key]
            if type(data[fileinfo][key]) == float:
              data[fileinfo][key] = f"{data[fileinfo][key]:.2f}"

    if not 'DetectedStars' in data[fileinfo].keys():
      for key in activeKeys:
        data[fileinfo][key] = 'None'

def targetStatus():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  return(data)

def generateJson():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data,True)
  for item in data:
    data[item]['filename'] = str(data[item]['filename'])
  return(data)
