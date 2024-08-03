#!/usr/bin/env python3
import sys
import json
import imageData
from datetime import datetime
from pathlib import Path
import re

try:
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

activeKeys = 'ExposureStart','Duration','DetectedStars', 'Eccentricity','FilterName','Duration','Binning','Gain','HFR','FWHM','GuidingRMSArcSec','GuidingRMSRAArcSec','GuidingRMSDECArcSec'

def addMetaData(data):
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
      if Path(metadataRecord["FilePath"]).name == Path(data[fileinfo]['filename']).name:
        for key in activeKeys:
          if key in metadataRecord.keys():
            data[fileinfo][key] = metadataRecord[key]
            if type(data[fileinfo][key]) == float:
              data[fileinfo][key] = f"{data[fileinfo][key]:.2f}"
          else:
            data[fileinfo][key] = 'None'
    if not 'DetectedStars' in data[fileinfo].keys():
      for key in activeKeys:
        data[fileinfo][key] = 'None'

def targetStatus():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  return(data)
