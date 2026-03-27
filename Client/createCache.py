import concurrent.futures
from pathlib import Path
import os

from astropy.io import fits
import json
import cv2
from auto_stretch import apply_stretch
from PIL import Image
import psutil

def convertFits(file):
  image={}
  header = fits.getheader(file)
  image['filter'] = header.get('FILTER', 'unknown')
  if "BAYERPAT" in header:
    image['bayerpat'] = header['BAYERPAT']
  image['object'] = header['OBJECT']
  image['telescope'] = header['TELESCOP']
  if image['telescope'] in config["shortNames"]:
    image['telescope'] = config["shortNames"][image['telescope']]
  image['exposure'] = header['EXPOSURE']
  image['date'] = header['DATE-LOC'].split('.')[0].replace('T', ' ')
  image['pierside'] = header.get('PIERSIDE', 'unknown')
  if 'ROTATOR' in header:
    image['rotator'] = str(int(header['ROTATOR']))
  else:
    image['rotator'] = 'not found'
  image['objectrotation'] = header['OBJCTROT']
  image['objectra'] = header['OBJCTRA']
  image['objectdec'] = header['OBJCTDEC']
  image['adumean'] = 0
  image['detectedstars'] = 0
  image['fwhm'] = 0
  image['hfr'] = 0
  image['eccentricity'] = 0
  image['guidingrmsarcsec'] = 0

  if 'MOONANGL' in header:
    image['moonangle'] = str(int(header['MOONANGL']))
  else:
    image['moonangle'] = 'not found'
  if file.name in imageMetaData:
    if 'ADUMean' in imageMetaData[file.name]:
      image['adumean'] = imageMetaData[file.name]['ADUMean']
    if 'DetectedStars' in imageMetaData[file.name]:
      image['detectedstars'] = imageMetaData[file.name]['DetectedStars']
    if 'FWHM' in imageMetaData[file.name]:
      image['fwhm'] = imageMetaData[file.name]['FWHM']
    if 'HFR' in imageMetaData[file.name]:
      image['hfr'] = imageMetaData[file.name]['HFR']
    if 'Eccentricity' in imageMetaData[file.name]:
      image['eccentricity'] = imageMetaData[file.name]['Eccentricity']
    if 'GuidingRMSArcSec' in imageMetaData[file.name]:
      image['guidingrmsarcsec'] = imageMetaData[file.name]['GuidingRMSArcSec']

  image['cachePath'] = (cacheDirectory / image['object'] / file.name).with_suffix('.jpg')
  if not image['cachePath'].parent.exists():
    image['cachePath'].parent.mkdir(parents=True, exist_ok=True)
  if not image['cachePath'].exists():
    data = fits.getdata(file, ext=0)
    if 'bayerpat' in image:
      debayered = cv2.cvtColor(data, cv2.COLOR_BayerBGGR2BGR)
      gray_image = cv2.cvtColor(debayered, cv2.COLOR_BGR2GRAY)
      normalized = gray_image
      cv2.normalize(debayered, normalized, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
      stretched = apply_stretch(normalized, target_bkg=0.15)
    else:
      normalized = data
      cv2.normalize(data, normalized, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
      stretched = apply_stretch(normalized, target_bkg=0.15)

    im = Image.fromarray(stretched * 255)
    im = im.convert('RGB')
    im = im.resize((im.width//2,im.height//2))
    if image['pierside'] == 'East':
      im = im.rotate(180)
    exif = im.getexif()
    persistedTags = {}
    persistedTags['date'] = image['date']
    persistedTags['object'] = image['object']
    persistedTags['telescope'] = image['telescope']
    persistedTags['filter'] = image['filter']
    persistedTags['pierside'] = image['pierside']
    persistedTags['rotator'] = image['rotator']
    persistedTags['adumean'] = image['adumean']
    persistedTags['detectedstars'] = image['detectedstars']
    persistedTags['fwhm'] = image['fwhm']
    persistedTags['hfr'] = image['hfr']
    persistedTags['exposure'] = image['exposure']
    persistedTags['objectrotation'] = image['objectrotation']
    persistedTags['objectra'] = image['objectra']
    persistedTags['objectdec'] = image['objectdec']
    persistedTags['eccentricity'] = image['eccentricity']
    persistedTags['guidingrmsarcsec'] = image['guidingrmsarcsec']
    exif[0x9286] = json.dumps(persistedTags)
    im.save(image['cachePath'], exif=exif,quality="web_low")
  return f"Processed cache file for: {file}"

try:
  config = json.load(open(Path(__file__).parent / 'config.json'))
except:
  config = {}
  config["S3BucketName"] = "uploadsla"
  config["username"] = psutil.Process().username()
  config["lastUsedLocalDir"] = os.getcwd()
  config["lastUsedS3Dir"] = config["S3BucketName"] + ":/"
  config["shortNames"] = {}

for scope in ["cdk14","sqa55"]:
  workingDirectory = Path.home() / "Pictures" / scope
  cacheDirectory = Path.home() / "Pictures" / scope / "_cache"

  imageMetaData = {}
  for file in workingDirectory.rglob("ImageMetaData*.json"):
    imds={}
    try:
      imds = json.load(open(file))
    except:
      print(file)
      pass
    for imd in imds:
      imageMetaData[Path(imd['FilePath']).name] = imd

  if len(imageMetaData) > 0:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
      future_convertFits = { executor.submit(convertFits,file): file for file in workingDirectory.rglob("*.fits") }
      for future in concurrent.futures.as_completed(future_convertFits):
        try:
          print(future.result())
        except Exception as exc:
          print(f'generated an exception: {exc}')
