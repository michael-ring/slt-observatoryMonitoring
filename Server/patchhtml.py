#!/usr/bin/env python3
from pathlib import Path
import sys
import platform

try:
  sys.path.append('.')
  sys.path.append('..')
  from config import rootserver
except:
  print("rootserver configuration is missing in config.py")
  sys.exit(1)


def runningOnServer():
  return platform.uname().node == rootserver['nodename']

if runningOnServer():
  basedir = Path(rootserver['basedir']) / 'pages'
else:
  basedir = Path(__file__).parent.parent / "Test"

for source in basedir.glob("*.html"):
  cleantarget = source.with_suffix(".cleanhtml")
  content = source.read_text()
  if content.find("<!-- include ") > -1:
    cleantarget.write_text(content)

  if cleantarget.exists():
    content = cleantarget.read_text()
    while content.find("<!-- include ") > -1:
      start = content.find(f"<!-- include ")
      end = content.find(" -->", start)
      sourceFile = content[start+13:end]
      newContent = (basedir / sourceFile).read_text()
      content = content[:start] + newContent + content[end+4:]

    source.write_text(content)

