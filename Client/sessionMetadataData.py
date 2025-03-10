#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import hashlib
import re

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope
from Client import imageData

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
      logger.error(f"MetaData file not found based on {Path(data[fileinfo]['FileName']).parent}")
      print(f"MetaData file not found based on {Path(data[fileinfo]['FileName']).parent}")
      raise Exception("MetaData file not found based on {Path(data[fileinfo]['FileName']).parent}")
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
    results = fileDateRegex.findall(Path(fileinfo['FileName']).name)
    if len(results) == 1:
      fileinfo['acquireddate'] = results[0][0:10]+' '+results[0][11:13]+':'+results[0][14:16]+':'+results[0][17:19]


def targetStatus():
  data = imageData.findMostRecentFitsFiles()
  result=[]
  tempresult={}
  for item in data:
    try:
      fitsHeader = imageData.extractFitsHeaders(item['FileName'])
      if fitsHeader.get('IMAGETYP') == 'LIGHT':
        if 'READOUTM' in fitsHeader:
          key = f"{fitsHeader['OBJECT']}-{fitsHeader['EXPOSURE']}-{fitsHeader['FILTER']}-{fitsHeader['GAIN']}-{fitsHeader['READOUTM']}"
        else:
          key = f"{fitsHeader['OBJECT']}-{fitsHeader['EXPOSURE']}-{fitsHeader['FILTER']}-{fitsHeader['GAIN']}"

        if key not in tempresult:
          tempresult[key]={
                     'desired': -1,
                     'acquired': 0,
                     'targetname': fitsHeader['OBJECT'],
                     'ra': fitsHeader['OBJCTRA'].split()[0]+(fitsHeader['OBJCTRA'].split()[1]*60+fitsHeader['OBJCTRA'].split()[2])/3600,
                     'dec': fitsHeader['OBJCTDEC'].split()[0]+(fitsHeader['OBJCTDEC'].split()[1]*60+fitsHeader['OBJCTDEC'].split()[2])/3600,
                     'overrideexposureorder': None,
                     'projectname': fitsHeader['OBJECT'],
                     'description': None,
                     'projectstate': 2,
                     'priority': 1,
                     'minimumaltitude': None,
                     'templatename': f"{fitsHeader['FILTER']}-{int(fitsHeader['EXPOSURE'])}",
                     'rotation': fitsHeader['OBJCTROT'],
                     'gain': fitsHeader['GAIN'],
                     'exposure': fitsHeader['EXPOSURE'],
                     'filtername': fitsHeader['FILTER'],
                     }
        if 'READOUTM' in fitsHeader:
          tempresult[key]['readoutmode'] = fitsHeader['READOUTM']
        else:
          tempresult[key]['readoutmode'] = None

        tempresult[key]['acquired'] += 1
    except:
      logger.exception(f"Failed to extract fits data from {item['FileName']}")
  for item in tempresult:
    result.append(tempresult[item])
  return result

def generateJson():
  data = imageData.findMostRecentFitsFiles()
  addMetaData(data)
  for item in data:
    item['FileName'] = str(item['FileName'])
  return data


if __name__ == '__main__':
  targetStatus()
