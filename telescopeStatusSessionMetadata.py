#!/usr/bin/env python3
import sys
from yattag import Doc
import platform
import sessionMetadataData
from pathlib import Path
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings(action="ignore", category=CryptographyDeprecationWarning)
from fabric import Connection
import imageData
import roofData
import allskyData

try:
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

try:
  from config import rootserver
except:
  print("rootserver configuration is missing in config.py")
  sys.exit(1)

def generateData():
  lastImages = sessionMetadataData.targetStatus()
  doc, tag, text = Doc().tagtext()
  doc.asis(f'<!-- begin include status-{telescope["shortname"]}.include -->')

  with tag('section'):
    doc.attr(id="content", klass="body")
    with tag('h2'):
      text("Current Roof/All Sky Camera Status")
    text(f"Roof is {roofData.getRoofStatus()}")
    allSkyFile=allskyData.findMostRecentAllSkyFile()
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

  if 'sshuser' in telescope.keys():
    sshuser=telescope['sshuser']
  else:
    sshuser=rootserver['username']
  c = Connection('slt-observatory.space',
                      user=sshuser,
                      connect_kwargs={'key_filename': telescope['sshkey'], })

  result = c.put(f"status-{telescope['shortname']}.include",remote=f"includes-{telescope['shortname']}/")
  print("Uploaded {0.local} to {0.remote}".format(result))

  sftp = c.client.open_sftp()
  list = sftp.listdir(f"frames-{telescope['shortname']}")
  sftp.close()

  for image in lastImages:
    if not ( Path(lastImages[image]['filename']).with_suffix('.jpg').name in list):
      imageData.convertFitsToJPG(lastImages[image]['filename'],lastImages[image]['filename'].with_suffix('.jpg'))
      result = c.put(lastImages[image]['filename'].with_suffix('.jpg'),remote=f"frames-{telescope['shortname']}/")
      print("Uploaded {0.local} to {0.remote}".format(result))
      lastImages[image]['filename'].with_suffix('.jpg').unlink()

  for file in Path(f'{telescope['statusfiles']}').glob("*.txt"):
    result = c.put(file,remote=f"statusfiles-{telescope['shortname']}/")
    print("Uploaded {0.local} to {0.remote}".format(result))
  if allSkyFile != None:
    ctime = allSkyFile.stat().st_ctime
    result = c.put(allSkyFile,remote=f"allsky-{telescope['shortname']}/allsky-{ctime}.jpg")
    print("Uploaded {0.local} to {0.remote}".format(result))
  c.close()
StgenerateData()