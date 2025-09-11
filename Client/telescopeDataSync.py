#!/usr/bin/env python3
import sys
from rclone_python import rclone
from pathlib import Path

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope
from Common.config import idrive
import discordHelper


def sync():
  rcloneUser = idrive[telescope['shortname']]['username']
  discordHelper.sendDiscordMessage("Starting Sync to Cloud")
  directories = Path(telescope['imagebasedir']).glob("????-??-??")
  for directory in directories:
    if directory.is_dir():
      targetDirs = directory.glob("*")
      for targetDir in targetDirs:
        targetName = targetDir.name
        targetDate = directory.name
        rcloneUploadDir = idrive[telescope['shortname']]['bucket']+'/'+targetName+'/'+targetDate
        print(f"Syncing {targetName} to {rcloneUploadDir}")
        rclone.copy(str(directory / targetName), rcloneUser+":/"+rcloneUploadDir)

  rcloneUser = idrive[telescope['shortname']]['cacheusername']
  rcloneUploadDir = f"{idrive[telescope['shortname']]['cachebucket']}/{telescope['shortname']}"
  print(f"Syncing _cache to {rcloneUploadDir}")
  rclone.copy(str(Path(telescope['imagebasedir']) / "_cache/"), rcloneUser+":/"+str(rcloneUploadDir))

  discordHelper.sendDiscordMessage("Sync to Cloud done")


if __name__ == '__main__':
  sync()
