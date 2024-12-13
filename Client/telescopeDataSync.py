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
  directories = Path(telescope['imagebasedir']).glob("????-??-??")
  for directory in directories:
    if directory.is_dir():
      targetDirs = directory.glob("*")
      for targetDir in targetDirs:
        targetName = targetDir.name
        targetDate = directory.name
        rcloneUser = idrive[telescope['shortname']]['username']
        rcloneUploadDir = idrive[telescope['shortname']]['bucket']+'/'+targetName+'/'+targetDate
        print(f"Syncing {targetName} to {rcloneUploadDir}")
        rclone.copy(str(directory / targetName), rcloneUser+":/"+rcloneUploadDir)


if __name__ == '__main__':
  sync()
