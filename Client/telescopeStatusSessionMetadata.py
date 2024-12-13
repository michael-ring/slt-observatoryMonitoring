#!/usr/bin/env python3
import json
import sys

from pathlib import Path
from Client import allskyData, roofData, sessionMetadataData, phd2Data
from Common import uploadData

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)


def uploadJson():
  allSkyJson = allskyData.generateJson()
  uploadFiles = allskyData.findAllSkyFiles()
  allSkyJsonFile = Path(__file__).parent.parent / 'Temp' / 'allSkyFiles.json'
  allSkyJsonFile.write_text(json.dumps(allSkyJson, indent=2))

  lastImages = sessionMetadataData.generateJson()
  lastImagesJsonFile = Path(__file__).parent.parent / 'Temp' / 'lastImages.json'
  lastImagesJsonFile.write_text(json.dumps(lastImages, indent=2))
  for lastImage in lastImages:
    uploadFiles.append(Path(lastImages[lastImage]['FileName']))
  phdStatus = phd2Data.generateJson()
  phdStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'phdStatus.json'
  phdStatusJsonFile.write_text(json.dumps(phdStatus, indent=2))
  uploadData.uploadData([lastImagesJsonFile, allSkyJsonFile, phdStatusJsonFile], uploadFiles)
  pass

if __name__ == '__main__':
  uploadJson()