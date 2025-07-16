#!/usr/bin/env/python3
import sys
import sqlite3
sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope

def query(queryString):
  logger.debug(f"Query: {queryString}")
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  data = con.execute(queryString)
  result = (data.fetchall())
  unpacked = [{k: item[k] for k in item.keys()} for item in result]
  con.close()
  logger.debug(f"ResultCount: {len(unpacked)}")
  return unpacked


dataset = query("""
SELECT 
  p.id as projectid,
  p.name as name, 
  p.description as description, 
  p.state as state, 
  p.priority as priority, 
  p.minimumtime as minimumtime, 
  p.minimumaltitude as minimumaltitude, 
  p.usecustomhorizon as usecustomhorizon, 
  p.horizonoffset as horizonoffset, 
  p.meridianwindow as meridianwindow, 
  p.filterswitchfrequency as filterswitchfrequency,
  p.ditherevery as ditherevery, 
  p.enablegrader as enablegrader, 
  p.isMosaic as ismosaic,
  p.flatshandling as flatshandling,
  p.smartexposureorder as smartexposureorder,
  t.Id as targetid,
  t.name as targetname,
  t.active as targetactive,
  t.ra as ra,
  t.dec as dec,
  t.rotation as rotation
FROM 
  project p, target t
WHERE
  p.Id = t.projectId
ORDER BY
  p.name
""")

for index,data in enumerate(dataset):
  print(f"Working on Project {data['name']}")
  ruleweights={}
  for row in query(f"""
SELECT 
  r.name as rulename, 
  r.weight as ruleweight 
FROM 
  ruleweight r
WHERE
  r.projectid = {data['projectid']}
ORDER BY
  r.Id
"""):
    ruleweights[row['rulename']] = row['ruleweight']


  if data['name'].count('_') != 1:
    print("  ERROR: Project name must contain exactly one '_' character")
    sys.exit(1)

  if data['name'].endswith('_S') or data['name'].endswith('_H') or data['name'].endswith('_O') or data['name'].endswith('_SH') or data['name'].endswith('_RGB') or data['name'].endswith('_LRGB'):
    realname = data['name'].split('_')[0]
    activefilters = data['name'].split('_')[1]
  else:
    print("  ERROR: Project name must end with _S or _H or _O or _SH or _RGB or _LRGB")
    sys.exit(1)
  if data['description'] == None:
    print("  WARNING: Description should not be empty")

  exposures = query(f"""
  SELECT 
    e.desired as desired, 
    et.filtername as filtername 
  FROM 
    exposureplan e, exposuretemplate et
  WHERE
    e.targetId = {data['targetid']}
  AND
    e.exposureTemplateId = et.Id
  """)
  for exposure in exposures:
    if exposure['desired'] == 0:
      print(f"  ERROR: Filter {exposure['filtername']} has 0 desired frames")
      sys.exit(1)
    if exposure['filtername'][0] not in activefilters:
      print(f"  ERROR: Filter {exposure['filtername']} is missing in Projectname")
      sys.exit(1)
  for char in activefilters:
    filterfound = False
    for exposure in exposures:
      if exposure['filtername'][0] == char:
        filterfound = True
    if not filterfound:
      print(f"  ERROR: Filter {char} from Projectname is missing in Exposure list")
      sys.exit(1)
  panneledprojects = 0
  for data2 in dataset:
    if data2['name'] == data['name']:
      panneledprojects += 1
  if panneledprojects > 1:
    panelproject = True
  else:
    panelproject = False

  if 'L' in activefilters or 'RGB' in activefilters or 'O' == activefilters:
    if data['priority'] != 2:
      print("  ERROR: priority for Broadband Targets must be 2")
      sys.exit(1)
    if activefilters == 'O':
      if ruleweights['Project Priority'] >80.0:
        print("  WARNING: project priority should be 80 or lower")
    else:
      if ruleweights['Project Priority'] <=80.0:
        print("  WARNING: project priority should be higher than 80")

  if data['minimumaltitude'] == 0.0:
    print("  WARNING: minimum altitude should be higher than 0.0")
  for value in 'usecustomhorizon','horizonoffset','meridianwindow','filterswitchfrequency','ditherevery','enablegrader','flatshandling','smartexposureorder':
    if data[value] > 0:
      print(f"  WARNING: unusual number {data[value]} for {value}")
  if 'S' in activefilters or 'H' in activefilters:
    if data['priority'] != 1:
      print("  WARNING: priority for Narrowband Targets must be 1")
      sys.exit(1)
  for rule in ruleweights:
    if rule == 'Setting Soonest':
      if ruleweights[rule] != 50.0:
        print("  WARNING: setting soonest should be 50")
    elif rule == 'Project Priority':
      pass
    elif rule == 'Mosaic Completion':
      if panelproject and ruleweights[rule] != 50.0:
        print("  WARNING: priority for Mosaic Completion should be 50")
      if not panelproject and ruleweights[rule] != 0.0:
        print("  ERROR: priority for Mosaic Completion should be 0 as this is not a Mosaic")
        sys.exit(1)
    else:
      if ruleweights[rule] != 0.0:
        print(f"  WARNING: Unusual setting of {ruleweights[rule]} found for {rule}")
  pass
print("All done")