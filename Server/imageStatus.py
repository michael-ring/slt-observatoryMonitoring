#!/usr/bin/env python3
import sys
import json
from yattag import Doc
from pathlib import Path, PureWindowsPath
from datetime import datetime,timedelta

sys.path.append('.')
sys.path.append('..')
from Common.config import telescopes,rootserver,logger,runningOnServer
import Server.allSkyStatus


def genDiv(telescopeName):
  ninaLoggingWhiteList = [
    ["INFO", "AscomTelescope.cs", 382, "telescopeInfo", ""],
    ["INFO", "CenterAfterDriftTrigger.cs", 189, "telescopeInfo", ""],
    ["INFO", "ImageSolver.cs", 41, "astapInfo", ""],
    ["INFO", "SafetyMonitorVM.cs", 94, "ninaInfo", ""],
    ["INFO", "SequenceItem.cs", 208, "afInfo", "Autofocus"],
    ["INFO", "SequenceItem.cs", 208, "phd2Info", "Dither"],
    ["INFO", "SequenceItem.cs", 254, "afInfo", "Autofocus"],
    ["INFO", "SequenceTrigger.cs", 114, "afInfo", "Autofocus"],
    ["INFO", "SequenceTrigger.cs", 114, "astapInfo", "CenterAfterDrift"],
    ["INFO", "SequenceTrigger.cs", 114, "ninaInfo", ""],
    ["INFO", "TelescopeVM.cs", 281, "telescopeInfo", ""],
    ["INFO", "TelescopeVM.cs", 338, "telescopeInfo", ""],
    ["ERROR", "PHD2Guider.cs", 202, "phd2Error", ""],
    ["ERROR", "PHD2Guider.cs", 356, "phd2Error", ""],
    ["ERROR", "SequenceFailureMonitor.cs", 55, "ninaError", ""],
    ["ERROR", "SequenceItem.cs", 195, "astapError", "CenterAndRotate"],
    ["ERROR", "SequenceItem.cs", 195, "afError", "Autofocus"],
    ["ERROR", "SequenceTrigger.cs", 132, "astapError", "CenterAndRotate"],
    ["ERROR", "SequenceTrigger.cs", 132, "afError", "Autofocus"],
    ["ERROR", "SequenceTrigger.cs", 132, "ninaError", ""],
    ["ERROR", "", -1, "ninaError", ""],
  ]

  ninaData = dict()
  imageData = dict()
  if runningOnServer():
    if Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/lastImagesStatus.json').exists():
      with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/lastImagesStatus.json')) as f:
        _imageData = json.load(f)
    if Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/ninaStatus.json').exists():
      with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/ninaStatus.json')) as f:
        _ninaData = json.load(f)
  else:
    if (Path(__file__).parent.parent / f'Test/{telescopeName}-data/lastImagesStatus.json').exists():
      with open(Path(__file__).parent.parent / f'Test/{telescopeName}-data/lastImagesStatus.json') as f:
        _imageData = json.load(f)
    if (Path(__file__).parent.parent / f'Test/{telescopeName}-data/ninaStatus.json').exists():
      with open(Path(__file__).parent.parent / f'Test/{telescopeName}-data/ninaStatus.json') as f:
        _ninaData = json.load(f)

  if _imageData == []:
    logger.info(f'No image data found for telescope {telescopeName}, early exit...')
    return ""

  for image in _imageData:
    imageData[datetime.strptime(image['acquireddate'], '%Y-%m-%d %H:%M:%S')] = image
  imageData=dict(reversed(sorted(imageData.items())))
  lastImageDate=next(iter(imageData.keys()))
  if lastImageDate.time().hour < 12:
    minFirstImageDate=(lastImageDate-timedelta(days=1)).replace(hour=12,minute=0,second=0)
  else:
    minFirstImageDate=lastImageDate.replace(hour=12,minute=0,second=0)

  imageData={}
  ninaData={}
  allSkyImages={}
  for image in _imageData:
    if datetime.strptime(image['acquireddate'], '%Y-%m-%d %H:%M:%S') > minFirstImageDate:
      imageData[datetime.strptime(image['acquireddate'], '%Y-%m-%d %H:%M:%S')] = image
  imageData=dict(reversed(sorted(imageData.items())))
  firstImageDate=next(iter(reversed(imageData.keys())))

  logger.info(f'Count of loaded Nina Datasets: {len(_ninaData)}')
  for key,ninaItem in _ninaData.items():
    itemDate=datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
    if firstImageDate < itemDate and itemDate < lastImageDate:
      ninaData[itemDate]=ninaItem

  logger.info(f'Count of Nina Datasets in timeframe {firstImageDate} - {lastImageDate} : {len(_ninaData)}')

  allSkyImages=Server.allSkyStatus.getAllSkyFrames(telescopeName,startTime=firstImageDate,endTime=lastImageDate+timedelta(hours=1))
  hasAllSkyImages=len(allSkyImages) > 0

  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Images Status")
    with tag('table'):
      with tag('thead'):
        with tag('tr'):
          for title in 'Time', 'Target', 'Exposure', 'Filter', 'Angle', 'Median', 'Stars', 'HFR', 'Roundness', 'Guiding', 'Thumbnail':
            with tag('th'):
              text(title)
              if title == 'Target':
                doc.attr(width='100%')
              else:
                doc.attr(width='1%')
          if hasAllSkyImages:
            with tag('th'):
              text('AllSky')
              doc.attr(width='1%')

      with tag('tbody', id='selector'):
        for imageDate,data in imageData.items():
          issueList = []
          if 'RotatorPosition' not in data:
            data['RotatorPosition'] = 'Unknown'
          # Work around issue that with_suffix does create issues when ° is in the filename
          imgStem = str(Path(f'{telescopeName}-images') / PureWindowsPath(data['FileName']).stem)
          realImageName = PureWindowsPath(data['FileName']).name
          imgPath = imgStem+'.jpg'
          imgThumb = imgStem+'.thumb.jpg'

          if len(ninaData) > 0:
            lastNinaDate = next(reversed(ninaData))
            while (lastNinaDate > imageDate):
              key = next(reversed(ninaData))
              for item in ninaLoggingWhiteList:
                if ninaData[key]['Level'].upper() == item[0]:
                  if ninaData[key]['Source'] == item[1]:
                    if int(ninaData[key]['Line']) == item[2]:
                      if len(item[4]) > 0:
                        if item[4] in ninaData[key]['Message']:
                          issueList.append({item[3]: f"{key.strftime('%H:%M:%S')} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                          break
                      else:
                        issueList.append({item[3]: f"{key.strftime('%H:%M:%S')} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                        break
                  else:
                    if item[2] == -1:
                      issueList.append({item[3]: f"{key.strftime('%H:%M:%S')} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                      break

              ninaData.popitem()
              if len(ninaData) == 0:
                break
              lastNinaDate = next(reversed(ninaData))
          if hasAllSkyImages:
            allSkyImage=Path("none.jpg")
            allSkyImageThumb=Path("none.thumb.jpg")
            for key,_allSkyImage in allSkyImages.items():
              if key >= imageDate:
                allSkyImage=_allSkyImage
                allSkyImageThumb = _allSkyImage.with_suffix('.thumb.jpg')
                break

          imageProperties = f"""
          Timestamp: {data['acquireddate']} |
          Exposure: {data['ExposureDuration']}s |
          Filter: {data['FilterName']} |
          Rotation: {data['RotatorPosition']}° |
          Median: {data['ADUMedian']} |
          Stars: {data['DetectedStars']} |
          HFR: {data['HFR']} |
          Roundness: {data['Eccentricity']} |
          GuidingRMS {data['GuidingRMSArcSec']}" 
          Guiding RA RMS: {data['GuidingRMSRAArcSec']}" 
          Guiding DEC RMS: {data['GuidingRMSDECArcSec']}"
        """
          with tag('tr'):
            with tag('td'):
              text(f"{data['acquireddate']}")
            with tag('td'):
              if 'targetname' not in data:
                data['targetname'] = Path(data['FilePath']).name.split(f"_{data['FilterName']}_")[0]
              text(f"{data['targetname']}")
              if len(issueList) > 0:
                doc.stag('br')
                for issue in issueList:
                  key=next(iter(issue))
                  if runningOnServer():
                    doc.stag('img',src=f'https://{rootserver['name']}/icons/{key}.png', title=issue[key], height=16)
                  else:
                    doc.stag('img', src=f'icons/{key}.png', title=issue[key], height=16)
            with tag('td'):
              text(f"{data['ExposureDuration']}")
            with tag('td'):
              text(f"{data['FilterName']}")
            with tag('td'):
              text(f"{data['RotatorPosition']}")
            with tag('td'):
              text(f"{data['ADUMedian']}")
            with tag('td'):
              text(f"{data['DetectedStars']}")
            with tag('td'):
              text(f"{data['HFR']}")
            with tag('td'):
              text(f"{data['Eccentricity']}")
            with tag('td'):
              text(f"{data['GuidingRMSArcSec']}/{data['GuidingRMSRAArcSec']}/{data['GuidingRMSDECArcSec']}")
            with tag('td'):
              if runningOnServer():
                doc.attr(('class','sub'),('data-src', f'https://{rootserver['name']}/images/{imgPath}'),
                         ('data-sub-html', f"<h4>{realImageName}</h4><p>{imageProperties}</p>"))
                doc.stag('img', src=f'https://{rootserver['name']}/images/{imgThumb}',height="50px")
              else:
                doc.attr(('class','sub'),('data-src', imgPath), ('data-sub-html', f"<h4>{realImageName}</h4><p>{imageProperties}</p>"))
                doc.stag('img', src=str(imgThumb),height="50px")
            if hasAllSkyImages:
              with tag('td'):
                if runningOnServer():
                  doc.attr(('class', 'allsky'), ('data-src', f'https://{rootserver['name']}/images/{telescopeName}-images/{Path(allSkyImage).name}'))
                  doc.stag('img', src=f'https://{rootserver['name']}/images/{telescopeName}-images/{Path(allSkyImageThumb).name}',height="50px")
                else:
                  doc.attr(('class','allsky'),('data-src', str(allSkyImage)))
                  doc.stag('img', src=str(allSkyImageThumb),height="50px")

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/pages/status-{telescopeName}.imageStatus.include'), mode='w') as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.imageStatus.include', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()

if __name__ == '__main__':
  genDiv('slt')

