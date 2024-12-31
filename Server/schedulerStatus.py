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

import skyPlot

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
    with open(Path(__file__).parent.parent / f'Test/{telescopeName}-data/schedulerStatus.json') as f:
      schedulerData = json.load(f)

  if schedulerData == []:
    return ""
  targetnames=[]
  hasMinimumaltitude = False
  hasMinimumtime = False
  hasReadoutmode = False
  for item in schedulerData:
    targetFound=False
    for target in targetnames:
      if item['targetname'] in target:
        targetFound = True
    if not targetFound:
      targetnames.append({item['targetname']: item['description']})
    if 'minimumaltitude' in item and item['minimumaltitude'] is not None:
      hasMinimumaltitude = True
    if 'minimumtime' in item and item['minimumtime'] is not None:
      hasMinimumtime = True
    if 'readoutmode' in item and item['readoutmode'] is not None:
      hasReadoutmode = True

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
  with (tag('section')):
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
          targetName = list(target.keys())[0]
          targetDescription = list(target.values())[0]
          with tag('tr'):
            with tag('td',style='vertical-align:top; width:750px'):
              with tag('h3'):
                if list(target.values())[0] != None:
                  text(f"{targetName} ({targetDescription})")
                else:
                  text(f"{targetName}")
              with tag('table',style='width:100%'):
                with tag('thead'):
                  with tag('tr'):
                    with tag('th'):
                      text('Filter')
                    with tag('th'):
                      text('Gain')
                    with tag('th'):
                      text('Exposure')
                    if hasReadoutmode:
                      with tag('th'):
                        text('ReadoutMode')
                    with tag('th'):
                      text('Rotation')
                    if hasMinimumaltitude:
                      with tag('th'):
                        text('Min Altitude')
                    if hasMinimumtime:
                      with tag('th'):
                        text('Min Time')
                    with tag('th'):
                      text('Count')
                with tag('tbody'):
                  for filtername in ['L','Lum','R','Red','G','Green','B','Blue','Sii','SII','SiiOiii','Ha','Halpha','HaOiii','Oiii','OIII']:
                    with tag('tr'):
                      for item2 in schedulerData:
                        if item2['targetname'] in target and item2['filtername'] == filtername:
                          if item2['acquired'] >= item2['desired']:
                            doc.attr(style='background-color: #88FF88')
                          if item2["overrideexposureorder"] is not None and not item2['overrideexposureorder'].startswith('Dither'):
                            doc.attr(style='background-color: #FF8888')
                          with tag('td'):
                            text(item2['filtername'])
                          with tag('td'):
                            text(item2['gain'])
                          with tag('td'):
                            text(item2['exposure'])
                          if hasReadoutmode:
                            with tag('td'):
                              text(item2['readoutmode'])
                          with tag('td'):
                            text(item2['rotation'])
                          if hasMinimumaltitude:
                            with tag('td'):
                              text(item2['minimumaltitude'])
                          if hasMinimumtime:
                            with tag('td'):
                              text(item2['minimumtime'])
                          with tag('td'):
                            if item2['desired'] > -1:
                              text(f"{item2['acquired']}/{item2['desired']}")
                            else:
                              text(f"{item2['acquired']}")
            with tag('td',style='width:280px'):
              for item3 in schedulerData:
                if item3['targetname'] in target:
                  targetra=item3['ra']
                  targetdec = item3['dec']
                  break
              if runningOnServer():
                fileName=Path(f'{rootserver['basedir']}/images/{telescopeName}-images/status-{telescopeName}.schedulerStatus.{targetName}.png'),
              else:
                fileName=Path(__file__).parent.parent / f'Test/status-{telescopeName}.schedulerStatus.{targetName}.png'
              skyPlot.sky_object_plot(targetra,targetdec,locations[telescope['location']],fileName)
              doc.stag('img',src=f'images/{telescopeName}-images/status-{telescopeName}.schedulerStatus.{targetName}.png',style='width:256px; height:256px')
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
