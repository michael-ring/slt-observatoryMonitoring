#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import subprocess
sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescope


logfile = Path( '/var/log/allsky.log' )
with logfile.open(encoding="utf-8") as f:
  contents = f.readlines()

lastdatestr=contents[-1].split(" ")[0][:19]
lastdate=datetime.fromisoformat(lastdatestr)
currentdate=datetime.now()
if currentdate > lastdate+timedelta(minutes=3):
  logger.info('Last log entry is older than 3 minutes, restarting allsky')
  logger.info('contents[-3]')
  logger.info('contents[-2]')
  logger.info('contents[-1]')
  subprocess.run(split('/usr/bin/sudo /usr/bin/systemctl restart allsky', shell=True))


