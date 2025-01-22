#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import traceback

sys.path.append('.')
sys.path.append('..')
from Common.config import logger, telescope
from Common import uploadData


def handle_exception(exc_type, exc_value, exc_traceback):
  if issubclass(exc_type, KeyboardInterrupt):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    return
  logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
  print(traceback.format_exc())


sys.excepthook = handle_exception


def uploadJson():
  uploadImageFiles = []
  uploadStatusFiles = []
  lastImages = []
  if 'schedulerdb' in telescope:
    logger.info('Generating TargetScheduler data')
    from Client import targetSchedulerData
    schedulerStatus = targetSchedulerData.targetStatus()
    schedulerStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'schedulerStatus.json'
    schedulerStatusJsonFile.write_text(json.dumps(schedulerStatus, indent=2))
    uploadStatusFiles.append(schedulerStatusJsonFile)
    lastImages = targetSchedulerData.lastImages()
  else:
    logger.info('Generating SessionMetaData data')
    from Client import sessionMetadataData
    from Common import locationData
    from Common.config import locations
    currentSunStatus = locationData.getSunData(locations[telescope['location']])
    if currentSunStatus['alt'] <= -12:
      schedulerStatus = sessionMetadataData.targetStatus()
      schedulerStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'schedulerStatus.json'
      schedulerStatusJsonFile.write_text(json.dumps(schedulerStatus, indent=2))
      uploadStatusFiles.append(schedulerStatusJsonFile)
      lastImages = sessionMetadataData.generateJson()
    else:
      logger.info('Sun is already up, not generating new data')

  if len(lastImages) > 0:
    logger.info('ImageData found, preparing upload')
    lastImagesStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'lastImagesStatus.json'
    lastImagesStatusJsonFile.write_text(json.dumps(lastImages, indent=2))
    uploadStatusFiles.append(lastImagesStatusJsonFile)
  else:
    logger.info('No Images found, not generating new data')

  acquiredDates = []
  logger.info('Collecting Dates of new images')
  for lastImage in lastImages:
    if Path(lastImage['FileName']).exists():
      uploadImageFiles.append(Path(lastImage['FileName']))
    if lastImage['acquireddate'][0:10] not in acquiredDates:
      acquiredDates.append(lastImage['acquireddate'][0:10])
      # The phd log may have started the day before, so also get logs from that day
      dayBefore = (datetime.strptime(lastImage['acquireddate'][0:10], '%Y-%m-%d') - timedelta(days=1)).strftime(
        '%Y-%m-%d')
      acquiredDates.append(dayBefore)
  for acquiredDate in acquiredDates:
    logger.info(f"Found {acquiredDate}")
  if 'phdlogbasedir' in telescope:
    logger.info('Collecting PHD data')
    from Client import phd2Data
    phd2Status = phd2Data.generateJson(acquiredDates)
    phd2StatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'phd2Status.json'
    phd2StatusJsonFile.write_text(json.dumps(phd2Status, indent=2))
    uploadStatusFiles.append(phd2StatusJsonFile)
  if 'ninalogbasedir' in telescope:
    logger.info('Collecting NINA data')
    from Client import ninaLogData
    ninaStatus = ninaLogData.generateJson(acquiredDates)
    if ninaStatus != {}:
      ninaStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'ninaStatus.json'
      ninaStatusJsonFile.write_text(json.dumps(ninaStatus, indent=2))
      uploadStatusFiles.append(ninaStatusJsonFile)
  if 'roofstatusdir' in telescope:
    logger.info('Collecting RoofStatus data')
    from Client import roofData
    roofStatus = roofData.generateJson()
    roofStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'roofStatus.json'
    roofStatusJsonFile.write_text(json.dumps(roofStatus, indent=2))
    uploadStatusFiles.append(roofStatusJsonFile)

  if 'weatherstatusdir' in telescope:
    logger.info('Collecting SkyAlert data')
    from Client import skyAlertData
    weatherStatus = skyAlertData.generateJson()
    weatherStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'weatherStatus.json'
    weatherStatusJsonFile.write_text(json.dumps(weatherStatus, indent=2))
    uploadStatusFiles.append(weatherStatusJsonFile)

  if 'powerbox' in telescope:
    logger.info('Collecting PowerBox data')
    from Client import powerBoxData
    powerBoxStatus = powerBoxData.generateJson()
    powerBoxStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'powerboxStatus.json'
    powerBoxStatusJsonFile.write_text(json.dumps(powerBoxStatus, indent=2))
    uploadStatusFiles.append(powerBoxStatusJsonFile)

  if 'allskybasedir' in telescope:
    logger.info('Collecting AllSky data')
    from Client import allskyData
    uploadAllSkyFiles = allskyData.findAllSkyFiles(acquiredDates)
  else:
    uploadAllSkyFiles = None

  logger.info('Uploading all data')
  uploadData.uploadData(uploadStatusFiles, uploadImageFiles, uploadAllSkyFiles)


if __name__ == '__main__':
  uploadJson()
