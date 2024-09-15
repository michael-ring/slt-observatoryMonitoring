import sys
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings(action="ignore", category=CryptographyDeprecationWarning)
from fabric import Connection
from Client import imageData

try:
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

try:
  from config import rootserver
except:
  print("rootserver configuration is missing in config.py")
  sys.exit(1)


def uploadData(dataFiles,imageFiles):
  if 'sshuser' in telescope.keys():
    sshuser=telescope['sshuser']
  else:
    sshuser=rootserver['sshuser']
  c = Connection('slt-observatory.space',
                      user=sshuser,
                      connect_kwargs={'key_filename': telescope['sshkey'], })
  c.create_session()
  #if not isinstance(dataFiles, list):
  #  dataFiles = [dataFiles]
  #if not isinstance(imageFiles,list):
  #  imageFiles = [imageFiles]
  sftp = c.client.open_sftp()
  try:
    sftp.mkdir(f"{telescope['shortname']}-data",mode=0o755)
  except:
    pass
  try:
    sftp.mkdir(f"{telescope['shortname']}-images",mode=0o755)
  except:
    pass
  list = sftp.listdir(f"{telescope['shortname']}-images")
  sftp.close()

  for dataFile in dataFiles:
    result = c.put(dataFile,remote=f"{telescope['shortname']}-data/")
    print("Uploaded {0.local} to {0.remote}".format(result))

  for imageFile in imageFiles:
    if not imageFile.with_suffix('.jpg').name in list:
      if imageFile.suffix == '.fits':
        imageData.convertFitsToJPG(imageFile, imageFile.with_suffix('.jpg'))
      result = c.put(imageFile.with_suffix('.jpg'),remote=f"{telescope['shortname']}-images/")
      print("Uploaded {0.local} to {0.remote}".format(result))
      if imageFile.suffix == '.fits':
        imageFile.with_suffix('.jpg').unlink()
