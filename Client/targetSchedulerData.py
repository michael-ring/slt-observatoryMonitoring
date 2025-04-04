#!/usr/bin/env python3
import sqlite3
import sys
import json
from datetime import datetime

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


def updatequery(queryString):
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  data = con.execute(queryString)
  con.commit()
  con.close()
  return True


def getHSTargets():
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%H' or p.name like '%S' or p.name like '%HS' or p.name like '%HSO' )
       
  ORDER BY
    projectstate asc, projectname asc
  """)
  return result


def getOTargets():
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%O' )
    AND
      ( p.name not like '%SHO' )
  ORDER BY
    projectstate asc, projectname asc
  """)
  return result


def getLRGBTargets():
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      ( p.state = 1 or p.state = 2 )
    AND
      ( p.name like '%RGB' OR p.name like '%LRGB' )
  ORDER BY
    projectstate asc, projectname asc
  """)
  return result

def getEnabledTargets():
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      ( p.state = 1 )
  ORDER BY
    projectname asc
  """)
  return result

def getDisabledTargets():
  result = query("""
  SELECT
    p.name as projectname,
    p.state as projectstate
  FROM 
    project p
  WHERE 
      ( p.state = 2 )
  ORDER BY
    projectname asc
  """)
  return result

def enableProject(projectName):
  projectName = projectName.replace("'", "''")
  return updatequery(f"""
  UPDATE 
    project 
  SET 
    state=1
  WHERE 
    name = '{projectName}'
  """)


def disableProject(projectName):
  projectName = projectName.replace("'", "''")
  return updatequery(f"""
  UPDATE 
    project 
  SET 
    state=2
  WHERE 
    name = '{projectName}'
  """)


def targetStatus():
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
  e.targetid = t.Id and e.exposureTemplateId = x.Id and t.projectid = p.id and ( p.state = 1 or p.state = 2 )
ORDER BY
  projectname asc, targetname asc
""")


def lastImages():
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
ORDER BY
  a.acquireddate desc
""")
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
