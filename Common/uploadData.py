import sys
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings(action="ignore", category=CryptographyDeprecationWarning)
from fabric import Connection
from Client import imageData
from pathlib import Path
from datetime import datetime

sys.path.append('.')
sys.path.append('..')
from Common.config import telescope,rootserver,logger

def uploadLogFile():
  logfile=None
  for handler in logger['root']['handlers']:
    if isinstance(handler, logging.FileHandler):
      logFile=handler['baseFilename']
  if logFile is not None:
    if 'sshuser' in telescope.keys():
      sshuser = telescope['sshuser']
    else:
      sshuser = rootserver['sshuser']
    c = Connection('slt-observatory.space', user=sshuser, connect_kwargs={'key_filename': telescope['sshkey'], })
    c.create_session()
    sftp = c.client.open_sftp()
    try:
      sftp.mkdir(f"{telescope['shortname']}-data", mode=0o755)
    except:
      pass
    sftp.close()
    result = c.put(filePath, remote=f"{telescope['shortname']}-data/")
    print("Uploaded {0.local} to {0.remote}".format(result))


def uploadData(dataFiles, imageFiles, allskyFiles=None):
  if 'sshuser' in telescope.keys():
    sshuser = telescope['sshuser']
  else:
    sshuser = rootserver['sshuser']
  c = Connection('slt-observatory.space', user=sshuser, connect_kwargs={'key_filename': telescope['sshkey'], })
  c.create_session()
  sftp = c.client.open_sftp()
  try:
    sftp.mkdir(f"{telescope['shortname']}-data", mode=0o755)
  except:
    pass
  try:
    sftp.mkdir(f"{telescope['shortname']}-images", mode=0o755)
  except:
    pass
  listing = sftp.listdir(f"{telescope['shortname']}-images")
  sftp.close()

  for dataFile in dataFiles:
    result = c.put(dataFile, remote=f"{telescope['shortname']}-data/")
    print("Uploaded {0.local} to {0.remote}".format(result))

  # Take the latest image and always upload it as subimage.jpg
  if len(imageFiles) > 0:
    imageData.convertFitsToJPG(imageFiles[0], imageFiles[0].with_stem('subimage').with_suffix('.jpg'))
    result = c.put(imageFiles[0].with_stem('subimage').with_suffix('.jpg'), remote=f"{telescope['shortname']}-images/")
    print("Uploaded {0.local} to {0.remote}".format(result))
    imageFiles[0].with_stem('subimage').with_suffix('.jpg').unlink()

  for imageFile in imageFiles:
    if not imageFile.with_suffix('.jpg').name in listing:
      if imageFile.suffix == '.fits':
        imageData.convertFitsToJPG(imageFile, imageFile.with_suffix('.jpg'))
        imageData.convertFitsToJPGThumb(imageFile, imageFile.with_suffix('.thumb.jpg'))
      result = c.put(imageFile.with_suffix('.jpg'), remote=f"{telescope['shortname']}-images/")
      print("Uploaded {0.local} to {0.remote}".format(result))
      if imageFile.with_suffix('.thumb.jpg').exists():
        result = c.put(imageFile.with_suffix('.thumb.jpg'), remote=f"{telescope['shortname']}-images/")
        print("Uploaded thumb {0.local} to {0.remote}".format(result))
      if imageFile.suffix == '.fits':
        imageFile.with_suffix('.jpg').unlink()
        if imageFile.with_suffix('.thumb.jpg').exists():
          imageFile.with_suffix('.thumb.jpg').unlink()

  if allskyFiles is not None and len(allskyFiles) > 0:
    for allskyFile in allskyFiles:
      ctime=datetime.fromtimestamp(Path(allskyFile).stat().st_ctime).strftime('%Y%m%d%H%M%S')
      if not f'allsky-{ctime}.jpg' in listing:
        result = c.put(allskyFile, remote=f"{telescope['shortname']}-images/allsky-{ctime}.jpg")
        print("Uploaded {0.local} to {0.remote}".format(result))
    result = c.put(allskyFiles[-1], remote=f"{telescope['shortname']}-images/suballsky.jpg")
    print("Uploaded {0.local} to {0.remote}".format(result))

