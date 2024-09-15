#!/usr/bin/env python3
import sys
from Client import allskyData,targetSchedulerData,sessionMetadataData,phd2Data
from pathlib import Path

from Client.targetSchedulerData import lastImages
from Common import uploadData
import json
from datetime import datetime
from datetime import timedelta

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

try:
  from config import rootserver
except:
  print("rootserver configuration is missing in config.py")
  sys.exit(1)

def uploadJson():
  uploadImageFiles = []
  uploadStatusFiles = []
  if 'schedulerdb' in telescope:
    schedulerStatus = targetSchedulerData.targetStatus()
    lastImages = targetSchedulerData.lastImages()
  else:
    lastImages = sessionMetadataData.generateJson()

  schedulerStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'schedulerStatus.json'
  schedulerStatusJsonFile.write_text(json.dumps(schedulerStatus, indent=2))
  uploadStatusFiles.append(schedulerStatusJsonFile)

  lastImagesStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'lastImagesStatus.json'
  lastImagesStatusJsonFile.write_text(json.dumps(lastImages, indent=2))
  uploadStatusFiles.append(lastImagesStatusJsonFile)

  acquiredDates=[]
  for lastImage in lastImages:
    if Path(lastImage['FileName']).exists():
      uploadImageFiles.append(Path(lastImage['FileName']))
    if lastImage['acquireddate'][0:10] not in acquiredDates:
      acquiredDates.append(lastImage['acquireddate'][0:10])
      #The phd log may have started the day before, so also get logs from that day
      dayBefore=(datetime.strptime(lastImage['acquireddate'][0:10],'%Y-%m-%d')-timedelta(days=1)).strftime('%Y-%m-%d')
      acquiredDates.append(dayBefore)
  if 'phdlogbasedir' in telescope:
    phd2Status = phd2Data.generateJson(acquiredDates)
    phd2StatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'phd2Status.json'
    phd2StatusJsonFile.write_text(json.dumps(phd2Status, indent=2))
    uploadStatusFiles.append(phd2StatusJsonFile)

  if 'allskybasedir' in telescope:
    uploadImageFiles = uploadImageFiles + allskyData.findAllSkyFiles(acquiredDates)

  uploadData.uploadData(uploadStatusFiles,uploadImageFiles)

uploadJson()