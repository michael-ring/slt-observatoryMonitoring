#!/usr/bin/env python3
import sqlite3
import sys
import json
from datetime import datetime

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def query(queryString):
  con = sqlite3.connect(telescope['schedulerdb'])
  con.row_factory = sqlite3.Row
  data = con.execute(queryString)
  result = (data.fetchall())
  unpacked = [{k: item[k] for k in item.keys()} for item in result]
  con.close()
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
      ( p.name like '%_H' or p.name like '%_S' or p.name like '%_HS' )
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
      ( p.name like '%_O' )
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
      ( p.name like '%_RGB' OR p.name like '%_LRGB' )
  ORDER BY
    projectstate asc, projectname asc
  """)
  return result

def enableProject(projectName):
  return updatequery(f"""
  UPDATE 
    project 
  SET 
    state=1
  WHERE 
    name = '{projectName}'
  """)

def disableProject(projectName):
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
  e.desired as desired ,e.acquired as acquired ,e.accepted as accepted,
  t.name as targetname, 
  p.name as projectname,
  p.state as projectstate,
  x.name as templatename
FROM 
  exposureplan e, target t, exposuretemplate x, project p
WHERE 
  e.targetid = t.Id and e.exposureTemplateId = x.Id and t.projectid = p.id and ( p.state = 1 or p.state = 2 )
ORDER BY
  projectstate asc, projectname asc
""")

def lastImages():
  lastAcquiredDate=None
  lastAcquiredDatesCount=0
  data = query("""
SELECT 
  p.name as projectname, p.state as projectstate, t.name as targetname,
  a.acquireddate as acquireddate ,a.filtername as filtername ,a.accepted as accepted,a.rejectreason as rejectreason, a.metadata as metadata
FROM 
  acquiredimage a,project p, target t 
WHERE 
  p.Id = a.projectId and t.Id = a.targetId
ORDER BY
  a.acquireddate desc
""")
  for pos,row in enumerate(data):
    metadata=json.loads(row['metadata'])
    for meta in metadata:
      if isinstance(metadata[meta],float):
        row[meta] = f"{metadata[meta]:.2f}"
      else:
        row[meta] = metadata[meta]
    row['acquireddate'] = datetime.fromtimestamp(row['acquireddate']).strftime('%Y-%m-%d %H:%M:%S')
    row.pop('metadata')
    if lastAcquiredDatesCount < 5:
      if lastAcquiredDate != row['acquireddate'][0:10]:
        lastAcquiredDatesCount+=1
        lastAcquiredDate=row['acquireddate'][0:10]
    else:
      return data[:pos-1]
  return(data)