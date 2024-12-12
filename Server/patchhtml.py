#!/usr/bin/env python3
from pathlib import Path

basedir=Path("/var/www/slt-observatory.space/pages/")
for source in basedir.glob("*.include"):
  target=source.with_suffix(".html")
  cleantarget=source.with_suffix(".cleanhtml")
  content=target.read_text()
  if content.find("<!-- unprocessed version -->") > -1:
    cleantarget.write_text(content)
  content=cleantarget.read_text()
  additionalContent=source.read_text()
  start=content.find(f"<!-- begin include {source.name} -->")
  end=content.find(f"<!-- end include {source.name} -->")
  end=end+len(f"<!-- end include {source.name} -->")
  content = content[:start]+additionalContent+content[end:]
  target.write_text(content)
