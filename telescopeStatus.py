#!/usr/bin/env python3
import sys
from yattag import Doc
import platform
import targetSchedulerData
from pathlib import Path
from fabric import Connection

try:
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def generateData():
  status = targetSchedulerData.targetStatus()
  lastImages = targetSchedulerData.lastImages()
  doc, tag, text = Doc().tagtext()
  doc.asis(f'<!-- begin include status-{telescope['shortname']}.include -->')

  with tag('section'):
    doc.attr( id="content", klass="body" )
    with tag('h2'):
      text(f'Status of configured projects')
    with tag('table'):
      doc.attr(width="1000px")
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
    doc.attr(id="content", klass="body")
    with tag('h2'):
      text(f'Current Roof/All Sky Camera Status')
    text("Roof is closed")
  with tag('section'):
    doc.attr(id="content", klass="body")
    with tag('h2'):
      text(f'Last recorded Frame')

  with tag('section'):
    doc.attr( id="content", klass="body" )
    with tag('h2'):
      text(f'Status of last 50 images')
    with tag('table'):
      doc.attr(width="1000px")
      with tag('tr'):
        for title in "Date","Project","Target","Filter","Stars","Guiding","GuidingRA","GuidingDEC","HFR","Eccentricity","Accepted","Reject Reason":
          with tag('th'):
            text(title)
      for image in lastImages:
        with tag('tr'):
          for field in "acquireddate","projectname","targetname","FilterName","DetectedStars","GuidingRMS","GuidingRMSRA","GuidingRMSDEC","HFR","Eccentricity","accepted","rejectreason" :
            with tag('td'):
              text(image[field])

  doc.asis(f'<!-- end include status-{telescope['shortname']}.include -->')
  index=Path(f"status-{telescope['shortname']}.include")
  index.write_text(doc.getvalue())

  result = Connection('temp.michael-ring.org',
                      user="root",
                      connect_kwargs={"key_filename": "/Users/tgdrimi9/.ssh/id_rsa", }).put(f'status-{telescope['shortname']}.include',remote=f'/var/www/html/slt-observatory.space/pages/')
  print("Uploaded {0.local} to {0.remote}".format(result))
  print(result)

generateData()