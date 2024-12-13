#!/usr/bin/env python3
import sys
import json
import platform
from yattag import Doc
from pathlib import Path, PureWindowsPath

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

  if runningOnServer():
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/lastImagesStatus.json')) as f:
      imageData = json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/lastImagesStatus.json') as f:
      imageData = json.load(f)

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
        for data in imageData:
          # Work around issue that with_suffix does create issues when ° is in the filename
          imgStem = str(Path(f'{telescopeName}-images') / PureWindowsPath(data['FileName']).stem)
          realImageName = PureWindowsPath(data['FileName']).name
          imgPath = imgStem+'.jpg'
          imgThumb = imgStem+'.thumb.jpg'

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
            doc.attr(('data-src', imgPath), ('data-sub-html', f"<h4>{realImageName}</h4><p>{imageData}</p>"))
            with tag('td'):
              text(f"{data['acquireddate']}")
            with tag('td'):
              text(f"{data['targetname']}")
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
              with tag('img', src=str(imgThumb)):
                text("")

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/{telescopeName}-imageStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/{telescopeName}-imageStatus.html', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()
