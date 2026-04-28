#!/usr/bin/env python3
import sqlite3
import sys
import json
from datetime import datetime

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


def getProfileId():
  """Get the profileid for this telescope from config.
  If not set, attempt to auto-detect (single profile) or raise an error."""
  if 'profileid' in telescope:
    return telescope['profileid']
  # Fallback: if there's only one profile in the DB, use it
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  data = con.execute("SELECT DISTINCT profileid FROM project")
  profiles = data.fetchall()
  con.close()
  if len(profiles) == 1:
    pid = profiles[0]['profileid']
    logger.info(f"Auto-detected single profileid: {pid}")
    return pid
  else:
    profile_list = [p['profileid'] for p in profiles]
    logger.error(f"Multiple profiles found in scheduler DB: {profile_list}. "
                 f"Please set 'profileid' in config.json for telescope '{telescope.get('shortname', '?')}'")
    raise SystemExit(f"Multiple profiles found: {profile_list}. Set 'profileid' in config.json.")


def query(queryString, params=None):
  logger.debug(f"Query: {queryString}")
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  if params:
    data = con.execute(queryString, params)
  else:
    data = con.execute(queryString)
  result = (data.fetchall())
  unpacked = [{k: item[k] for k in item.keys()} for item in result]
  con.close()
  logger.debug(f"ResultCount: {len(unpacked)}")
  return unpacked


def updatequery(queryString, params=None):
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  if params:
    con.execute(queryString, params)
  else:
    con.execute(queryString)
  con.commit()
  con.close()
  return True


def getHSTargets():
  profileId = getProfileId()
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      p.profileid = ?
    AND
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%H' or p.name like '%S' or p.name like '%HS' or p.name like '%HSO' )
       
  ORDER BY
    projectstate asc, projectname asc
  """, (profileId,))
  return result


def getOTargets():
  profileId = getProfileId()
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      p.profileid = ?
    AND
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%O' )
    AND
      ( p.name not like '%SHO' )
  ORDER BY
    projectstate asc, projectname asc
  """, (profileId,))
  return result


def getLRGBTargets():
  profileId = getProfileId()
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      p.profileid = ?
    AND
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%RGB' OR p.name like '%LRGB' )
  ORDER BY
    projectstate asc, projectname asc
  """, (profileId,))
  return result

def getEnabledTargets():
  profileId = getProfileId()
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      p.profileid = ?
    AND
      ( p.state = 1 )
  ORDER BY
    projectname asc
  """, (profileId,))
  return result

def getDisabledTargets():
  profileId = getProfileId()
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      p.profileid = ?
    AND
      ( p.state = 2 )
  ORDER BY
    projectname asc
  """, (profileId,))
  return result

def enableProject(projectName):
  profileId = getProfileId()
  return updatequery("""
  UPDATE 
    project 
  SET 
    state=1
  WHERE 
    name = ? AND profileid = ?
  """, (projectName, profileId))


def disableProject(projectName):
  profileId = getProfileId()
  return updatequery("""
  UPDATE 
    project 
  SET 
    state=2
  WHERE 
    name = ? AND profileid = ?
  """, (projectName, profileId))


def targetStatus():
  profileId = getProfileId()
  return query("""
SELECT
  e.desired as desired,
  e.acquired as acquired,
  t.name as targetname,
  t.ra as ra,
  t.dec as dec,
  t.rotation as rotation,
  p.name as projectname,
  p.description as description,
  p.state as projectstate,
  p.priority as priority,
  p.minimumaltitude as minimumaltitude,
  p.minimumtime as minimumtime,
  x.name as templatename,
  x.filtername as filtername,
  x.gain as gain,
  x.readoutmode as readoutmode,
  x.defaultexposure as exposure
FROM 
  exposureplan e, target t, exposuretemplate x, project p
WHERE 
  e.targetid = t.Id and e.exposureTemplateId = x.Id and t.projectid = p.id 
  and p.profileid = ?
  and ( p.state = 1 or p.state = 2 )
ORDER BY
  projectname asc, targetname asc
""", (profileId,))


def lastImages():
  profileId = getProfileId()
  lastAcquiredDate = None
  lastAcquiredDatesCount = 0
  data = query("""
SELECT 
  p.name as projectname, 
  p.state as projectstate, 
  t.name as targetname,
  a.acquireddate as acquireddate ,
  a.filtername as filtername ,
  a.metadata as metadata
FROM 
  acquiredimage a,project p, target t 
WHERE 
  p.Id = a.projectId and t.Id = a.targetId
  and p.profileid = ?
ORDER BY
  a.acquireddate desc
""", (profileId,))
  for pos, row in enumerate(data):
    metadata = json.loads(row['metadata'])
    for meta in metadata:
      if isinstance(metadata[meta], float):
        row[meta] = f"{metadata[meta]:.2f}"
      else:
        row[meta] = metadata[meta]
    row['acquireddate'] = datetime.fromtimestamp(row['acquireddate']).strftime('%Y-%m-%d %H:%M:%S')
    row.pop('metadata')
    if lastAcquiredDatesCount < 5:
      if lastAcquiredDate != row['acquireddate'][0:10]:
        lastAcquiredDatesCount +=1
        lastAcquiredDate=row['acquireddate'][0:10]
    else:
      return data[:pos-1]
  return data
