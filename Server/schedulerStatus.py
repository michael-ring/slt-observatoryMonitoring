#!/usr/bin/env python3
import json
import platform
from asyncio.staggered import staggered_race

from yattag import Doc
from pathlib import Path
import sys

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import locations, telescopes, rootserver
except:
  print("locations configuration is missing in config.py")
  sys.exit(1)


def runningOnServer():
  return platform.uname().node == rootserver['nodename']


def genDiv(telescopeName):
  width, height = 1024, 200
  telescope = telescopes[telescopeName]
  localtz = locations[telescope['location']]['timezone']

  if runningOnServer():
    with open(Path(f'/home/{rootserver['sshuser']}/{telescopeName}-data/schedulerStatus.json')) as f:
      schedulerData = json.load(f)
  else:
    with open(Path(__file__).parent.parent / 'Test/vst-data/schedulerStatus.json') as f:
      schedulerData = json.load(f)

  targetnames=[]
  for item in schedulerData:
    if item['targetname'] not in targetnames:
      targetnames.append(item['targetname'])
  doc, tag, text = Doc().tagtext()
  doc.asis("""<!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
</style>
</head>
<body>
""")
  with tag('section'):
    doc.attr(id='content', klass='body')
    with tag('h2'):
      text("Scheduler Status")

    with tag('table',style='width:1024px'):
      #with tag('thead'):
      #  with tag('tr'):
      #    doc.stag('th',style='width:100%')
      #    doc.stag('th',style='width:256px')
      with tag('tbody'):
        for target in targetnames:
          with tag('tr'):
            with tag('td',style='vertical-align:top; width:750px'):
              with tag('h3'):
                text(target)
              with tag('table',style='width:100%'):
                with tag('thead'):
                  with tag('tr'):
                    with tag('th'):
                      text('Filter')
                    with tag('th'):
                      text('Gain')
                    with tag('th'):
                      text('Exposure')
                    with tag('th'):
                      text('ReadoutMode')
                    with tag('th'):
                      text('Rotation')
                    with tag('th'):
                      text('Min Altitude')
                    with tag('th'):
                      text('Min Time')
                    with tag('th'):
                      text('Count')
                with tag('tbody'):
                  for filtername in ['L','R','G','B','Sii','SiiOiii','Ha','HaOiii','Oiii']:
                    with tag('tr'):
                      for item in schedulerData:
                        if item['targetname'] == target and item['filtername'] == filtername:
                          if item['acquired'] == item['desired']:
                            doc.attr(style='background-color: #88FF88')
                          with tag('td'):
                            text(item['filtername'])
                          with tag('td'):
                            text(item['gain'])
                          with tag('td'):
                            text(item['exposure'])
                          with tag('td'):
                            text(item['readoutmode'])
                            with tag('td'):
                              text(item['rotation'])
                            with tag('td'):
                              text(item['minimumaltitude'])
                            with tag('td'):
                              text(item['minimumtime'])
                            with tag('td'):
                              text(f"{item['acquired']}/{item['desired']}")
            with tag('td',style='width:280px'):
              doc.stag('img',src=f'status-{telescopeName}.schedulerStatus.{target}.png',style='width:256px; height:256px')
  doc.asis('</body></html>')





  if runningOnServer():
    with open(Path(f'{rootserver['basedir']}/pages/status-{telescopeName}.schedulerStatus.include'), mode="w") as f:
      f.writelines(doc.getvalue())
  else:
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.schedulerStatus.include', mode='w') as f:
      f.writelines(doc.getvalue())
    with open(Path(__file__).parent.parent / f'Test/status-{telescopeName}.schedulerStatus.html', mode='w') as f:
      f.writelines(doc.getvalue())
  return doc.getvalue()


if __name__ == '__main__':
  genDiv('vst')
