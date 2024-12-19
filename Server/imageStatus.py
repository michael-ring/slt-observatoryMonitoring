#!/usr/bin/env python3
import sys
import json
import platform
from yattag import Doc
from pathlib import Path, PureWindowsPath
from datetime import datetime,timedelta

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import telescopes, rootserver
except:
  print("telescopes configuration is missing in config.py")
  sys.exit(1)

def runningOnServer():
  return platform.uname().node == rootserver['nodename']


def genDiv(telescopeName):
  ninaLoggingWhiteList = [
    ["INFO", "AscomTelescope.cs", 382, "telescopeInfo", ""],
    ["INFO", "ImageSolver.cs", 41, "astapInfo", ""],
    ["INFO", "SafetyMonitorVM.cs", 94, "ninaInfo", ""],
    ["INFO", "SequenceItem.cs", 208, "afInfo", "Autofocus"],
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
  if runningOnServer():
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/lastImagesStatus.json')) as f:
      imageData = json.load(f)
    if Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/ninaStatus.json').exists():
      with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/ninaStatus.json')) as f:
        ninaData = json.load(f)

  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/lastImagesStatus.json') as f:
      imageData = json.load(f)
      if (Path(__file__).parent.parent / 'Test/vst-data/ninaStatus.json').exists():
        with open(Path(__file__).parent.parent / 'Test/vst-data/ninaStatus.json') as g:
          ninaData = json.load(g)

  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Images Status")
    with tag('table'):
      with tag('thead'):
        with tag('tr'):
          for title in 'Time', 'Target', 'Duration', 'Filter', 'Rotation', 'Stars', 'HFR', 'Roundness', 'Guiding(ArcSec)', 'Thumbnail':
            with tag('th'):
              text(title)
              if title == 'Target':
                doc.attr(width='100%')
              else:
                doc.attr(width='1%')
      with tag('tbody', id='tb-tr'):
        firstPictureDate = datetime.strptime(imageData[0]['acquireddate'], '%Y-%m-%d %H:%M:%S') - timedelta(hours=12)
        for data in imageData:
          lastPictureDate = datetime.strptime(data['acquireddate'], '%Y-%m-%d %H:%M:%S')
          if lastPictureDate < firstPictureDate:
            break
          issueList = []
          # Work around issue that with_suffix does create issues when ° is in the filename
          imgStem = str(Path(f'{telescopeName}-images') / PureWindowsPath(data['FileName']).stem)
          realImageName = PureWindowsPath(data['FileName']).name
          imgPath = imgStem+'.jpg'
          imgThumb = imgStem+'.thumb.jpg'
          if len(ninaData) > 0:
            lastNinaDate = datetime.strptime(next(reversed(ninaData)), '%Y-%m-%d %H:%M:%S')
            while (lastNinaDate > lastPictureDate):
              key = next(reversed(ninaData))
              for item in ninaLoggingWhiteList:
                if ninaData[key]['Level'].upper() == item[0]:
                  if ninaData[key]['Source'] == item[1]:
                    if int(ninaData[key]['Line']) == item[2]:
                      if len(item[4]) > 0:
                        if item[4] in ninaData[key]['Message']:
                          issueList.append({item[3]: f"{key[-8:]} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                          break
                      else:
                        issueList.append({item[3]: f"{key[-8:]} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                        break
                  else:
                    if item[2] == -1:
                      issueList.append({item[3]: f"{key[-8:]} {ninaData[key]['Source']}({ninaData[key]['Line']}): {ninaData[key]['Message']}"})
                      break

              ninaData.popitem()
              if len(ninaData) == 0:
                break
              lastNinaDate = datetime.strptime(next(reversed(ninaData)), '%Y-%m-%d %H:%M:%S')

          imageData = f"""
          Timestamp: {data['acquireddate']} |
          Exposure: {data['ExposureDuration']}s |
          Filter: {data['FilterName']} |
          Rotation: {data['RotatorPosition']}° |
          Stars: {data['DetectedStars']} |
          HFR: {data['HFR']} |
          Roundness: {data['Eccentricity']} |
          GuidingRMS {data['GuidingRMSArcSec']}" 
          Guiding RA RMS: {data['GuidingRMSRAArcSec']}" 
          Guiding DEC RMS: {data['GuidingRMSDECArcSec']}"
        """
          with tag('tr'):
            if runningOnServer():
              doc.attr(('data-src', f'https://{rootserver['name']}{imgPath}'), ('data-sub-html', f"<h4>{realImageName}</h4><p>{imageData}</p>"))
            else:
              doc.attr(('data-src', imgPath), ('data-sub-html', f"<h4>{realImageName}</h4><p>{imageData}</p>"))
            with tag('td'):
              text(f"{data['acquireddate']}")
            with tag('td'):
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
              text(f"{data['DetectedStars']}")
            with tag('td'):
              text(f"{data['HFR']}")
            with tag('td'):
              text(f"{data['Eccentricity']}")
            with tag('td'):
              text(f"{data['GuidingRMSArcSec']}/{data['GuidingRMSRAArcSec']}/{data['GuidingRMSDECArcSec']}")
            with tag('td'):
              if runningOnServer():
                doc.stag('img', src=f'https://{rootserver['name']}{imgThumb}')
              else:
                doc.stag('img', src=str(imgThumb))

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/pages/status-{telescopeName}.imageStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.imageStatus.include', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()
