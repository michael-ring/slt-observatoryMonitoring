#!/usr/bin/env python3
import sys
import json
import platform
from yattag import Doc
from pathlib import Path

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
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/roofStatus.json')) as f:
      roofData = json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/roofStatus.json') as f:
      roofData = json.load(f)

  doc, tag, text = Doc().tagtext()
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Roof Status")
    with tag('table'):
      with tag('tr'):
        for title in 'Timestamp', 'Status':
          with tag('th'):
            text(title)
      for status in reversed(roofData):
        with tag('tr'):
          with tag('td'):
            text(f"{list(status.keys())[0]}")
          with tag('td'):
            text(f"{status[list(status.keys())[0]]['roof']}")

  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/{telescopeName}-skyAlertStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/{telescopeName}-skyAlertStatus.html', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()
