#!/usr/bin/env python3
import sys
from yattag import Doc
import platform
import targetSchedulerData
from pathlib import Path
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings(action="ignore", category=CryptographyDeprecationWarning)
from fabric import Connection
import imageData

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
  status = targetSchedulerData.targetStatus()
  lastImages = targetSchedulerData.lastImages()
  doc, tag, text = Doc().tagtext()
  doc.asis(f"<!-- begin include status-{telescope['shortname']}.include -->")

  with tag('section'):
    doc.attr( id='content', klass='body' )
    with tag('h2'):
      text("Status of configured projects")
    with tag('table'):
      doc.attr(width='1000px')
      with tag('tr'):
        for title in "Status","Project","Target","Template","Desired","Accepted","Acquired" :
          with tag('th'):
            text(title)
      for stat in status:
        with tag('tr'):
          with tag('td'):
            if stat['projectstate'] == 1:
              text("Active")
              #doc.asis("&#x2705;")
            else:
              text("Inactive")
              #doc.asis("&#x274e;")
          for field in "projectname","targetname","templatename","desired","accepted","acquired" :
            with tag('td'):
              text(stat[field])

  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text(f"Current Roof/All Sky Camera Status")
    text("Roof is closed")
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Last recorded Frame")
    with tag('img'):
      #latest=next(iter(lastImages))
      doc.attr(src=f"images/frames-{telescope['shortname']}/{Path(lastImages[0]['FileName']).stem.replace("°C","")}.jpg")
      doc.attr(alt=f"{Path(lastImages[0]['FileName']).stem.replace("°C","")}.jpg")

  with tag('section'):
    doc.attr( id='content', klass='body' )
    with tag('h2'):
      text("Status of last 50 images")
    with tag('table'):
      doc.attr(width='1000px')
      with tag('tr'):
        for title in "Date","Target","Filter","Gain","Duration","Stars","Guiding","GuidingRA","GuidingDEC","HFR","FWHM","Eccentricity":
          with tag('th'):
            text(title)
      for image in lastImages:
        with tag('tr'):
          for field in "acquireddate","targetname","FilterName","Gain","ExposureDuration","DetectedStars","GuidingRMSArcSec","GuidingRMSRAArcSec","GuidingRMSDECArcSec","HFR","FWHM","Eccentricity" :
            with tag('td'):
              text(image[field])

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
  result = c.put(f"status-{telescope['shortname']}.include",remote=f"{rootserver['basedir']}/pages/")
  print("Uploaded {0.local} to {0.remote}".format(result))

  sftp = c.client.open_sftp()
  list = sftp.listdir(f"{rootserver['basedir']}theme/images/frames-{telescope['shortname']}")
  sftp.close()
  for image in lastImages:
    if not ( Path(image['FileName']).with_suffix('.jpg').name in list):
      if Path(image['FileName']).exists():
        imageData.convertFitsToJPG(Path(image['FileName']),Path(image['FileName']).with_suffix('.jpg'))
        result = c.put(Path(image['FileName']).with_suffix('.jpg'),remote=f"{rootserver['basedir']}/images/frames-{telescope["shortname"]}/{Path(image['FileName']).stem.replace("°C","")}.jpg")
        print("Uploaded {0.local} to {0.remote}".format(result))
        Path(image['FileName']).with_suffix('.jpg').unlink()

generateData()