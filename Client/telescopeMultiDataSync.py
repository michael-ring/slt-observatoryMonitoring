import concurrent.futures
from pathlib import Path
import os
import json
import psutil
import py7zr


def compressFits(file):
  _zipfile = Path(file).with_suffix('.fits.7z')
  _tmpzipfile = _zipfile.with_suffix('.7ztemp')
  if not _zipfile.exists():
    try:
      with py7zr.SevenZipFile(_tmpzipfile, 'w', filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9}]) as archive:
        archive.writeall(file, arcname=file.name)
      _tmpzipfile.rename(_zipfile)
    except:
      return (f"Compress failed: {_zipfile}")
  return f"Compressed: {_zipfile}"


try:
  config = json.load(open(Path(__file__).parent / 'config.json'))
except:
  config = {}
  config["S3BucketName"] = "uploadsla"
  config["username"] = psutil.Process().username()
  config["lastUsedLocalDir"] = os.getcwd()
  config["lastUsedS3Dir"] = config["S3BucketName"] + ":/"
  config["shortNames"] = {}

for scope in ["cdk14"]:
  workingDirectory = Path.home() / "Pictures" / scope
  backupDirectory = Path.home() / "Desktop" / "backup"
  for file in workingDirectory.rglob("*.fits"):
    targetFile = backupDirectory / file.parent.parent.parent.name / file.parent.parent.name / file.parent.name / file.name
    print(f"Backing up File {file} to {targetFile}")
    targetFile.parent.mkdir(parents=True, exist_ok=True)
    if not targetFile.exists():
      targetFile.write_bytes(file.read_bytes())

  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_compressFits = {executor.submit(compressFits, file): file for file in workingDirectory.rglob("*.fits")}
    for future in concurrent.futures.as_completed(future_compressFits):
      try:
        print(future.result())
      except Exception as exc:
        print(f'generated an exception: {exc}')
