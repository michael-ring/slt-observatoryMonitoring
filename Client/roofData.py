#!/usr/bin/env python3
import sys
from pathlib import Path

try:
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def getRoofStatus():
  roofStatus = "closed"
  roofDataFile = Path(telescope['statusfiles']) / "RoofStatusFile.txt"
  if roofDataFile.exists():
    content=roofDataFile.read_text()
    if content.find("CLOSED") != -1:
      roofStatus = "closed"
    if content.find("OPEN") != -1:
      roofStatus = "open"
  return roofStatus
