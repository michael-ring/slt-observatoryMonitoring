#!/usr/bin/env python3
import sys
from rclone_python import rclone
from pathlib import Path
try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

from config import idrive

def sync():
  dirs=Path(telescope['imagebasedir']).glob("????-??-??")
  for dir in dirs:
    if dir.is_dir():
      targetDirs=dir.glob("*")
      for targetDir in targetDirs:
        targetName=targetDir.name
        targetDate=dir.name
        rcloneUser=idrive[telescope['shortname']]['username']
        rcloneUploadDir=idrive[telescope['shortname']]['bucket']+'/'+targetName+'/'+targetDate
        print(f"Syncing {targetName} to {rcloneUploadDir}")
        rclone.copy(str(dir / targetName),rcloneUser+":/"+rcloneUploadDir)

sync()