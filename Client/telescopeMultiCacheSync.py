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
  discordHelper.sendDiscordMessage("Starting Sync of Image Cache to Cloud")
  rcloneUser = idrive[telescope['shortname']]['cacheusername']
  rcloneUploadDir = f"{idrive[telescope['shortname']]['cachebucket']}"
  print(f"Syncing _cache to {rcloneUploadDir}")
  directory = Path(telescope['imagebasedir'])
  syncDir=Path(directory) / "cdk14/" / "_cache/"
  if syncDir.is_dir():
    rclone.copy(str(syncDir), rcloneUser+":/"+str(rcloneUploadDir)+"/CDK14/")
  else:
    print(f"{syncDir} not found, skipping")

  syncDir=Path(directory) / "sqa55/" / "_cache/"
  if syncDir.is_dir():
    rclone.copy(str(syncDir), rcloneUser+":/"+str(rcloneUploadDir)+"/speedy/")
  else:
    print(f"{syncDir} not found, skipping")

  discordHelper.sendDiscordMessage("Image Cache Sync to Cloud finished")


if __name__ == '__main__':
  sync()
