#!/usr/bin/env python3
import json
import sys

from yattag import Doc
from pathlib import Path
from Client import allskyData, roofData, sessionMetadataData,phd2Data
from Common import uploadData

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def uploadJson():
  allSkyJson = allskyData.generateJson()
  uploadFiles = allskyData.findMostRecentAllSkyFiles()
  allSkyJsonFile = Path(__file__).parent.parent / 'Temp' / 'allSkyFiles.json'
  allSkyJsonFile.write_text(json.dumps(allSkyJson, indent=2))

  lastImages = sessionMetadataData.generateJson()
  lastImagesJsonFile = Path(__file__).parent.parent / 'Temp' / 'lastImages.json'
  lastImagesJsonFile.write_text(json.dumps(lastImages, indent=2))
  for lastImage in lastImages:
    uploadFiles.append(Path(lastImages[lastImage]['filename']))
  phdStatus = phd2Data.generateJson()
  phdStatusJsonFile = Path(__file__).parent.parent / 'Temp' / 'phdStatus.json'
  phdStatusJsonFile.write_text(json.dumps(phdStatus, indent=2))
  uploadData.uploadData([lastImagesJsonFile,allSkyJsonFile,phdStatusJsonFile], uploadFiles)
  pass

def generateData():
  lastImages = sessionMetadataData.targetStatus()
  doc, tag, text = Doc().tagtext()
  doc.asis(f'<!-- begin include status-{telescope["shortname"]}.include -->')

  with tag('section'):
    doc.attr(id="content", klass="body")
    with tag('h2'):
      text("Current Roof/All Sky Camera Status")
    text(f"Roof is {roofData.getRoofStatus()}")
    allSkyFile= allskyData.findMostRecentAllSkyFile()
    if allSkyFile != None:
      ctime=allSkyFile.stat().st_ctime
      with tag('img'):
        doc.attr(src=f"images/allsky-{telescope['shortname']}/allsky-{ctime}.jpg")
        doc.attr(alt=f"AllSky-{ctime}")

  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Last recorded Image")
    with tag('img'):
      latest=next(iter(lastImages))
      doc.attr(src=f"images/frames-{telescope['shortname']}/{lastImages[latest]['filename'].stem}.jpg")
      doc.attr(alt=f"{lastImages[latest]['filename'].stem}.jpg")

  with tag('section'):
    doc.attr( id='content', klass='body' )
    with tag('h2'):
      text("Status of last 50 images")
    with tag('table'):
      doc.attr(width='1000px')
      with tag('tr'):
        for title in "Date","Filter","Gain","Duration","Stars","Guiding","GuidingRA","GuidingDEC","HFR","FWHM","Eccentricity":
          with tag('th'):
            text(title)
      for image in lastImages:
        with tag('tr'):
          for field in "ExposureStart","FilterName","Gain","Duration","DetectedStars","GuidingRMSArcSec","GuidingRMSRAArcSec","GuidingRMSDECArcSec","HFR","FWHM","Eccentricity":
            with tag('td'):
              text(lastImages[image][field])

  doc.asis(f"<!-- end include status-{telescope['shortname']}.include -->")
  index=Path(f"status-{telescope['shortname']}.include")
  index.write_text(doc.getvalue())

generateData()
uploadJson()