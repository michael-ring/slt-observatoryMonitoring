import platform
from pathlib import Path
import json
import sys
import logging.config

configFile=Path(__file__).parent.parent / "config.json"
loggingFile=Path(__file__).parent.parent / "monitoring.log"
if not configFile.is_file():
  print("config.json file not found in main folder")
  sys.exit(1)

try:
  config=json.load(configFile.open())
except json.decoder.JSONDecodeError as e:
  print("config.json has parsing errors, please fix!")
  print(e)
  sys.exit(1)

config['logging']['handlers']['info_file_handler']['filename'] = str(loggingFile)
logging.config.dictConfig(config['logging'])
logger = logging.getLogger(__name__)
logger.info('Start of logging')

def runningOnServer():
  if 'testing' in rootserver:
    return platform.uname().node == rootserver['nodename'] and rootserver['testing'] is not True
  else:
    return platform.uname().node == rootserver['nodename']

def genTelescopeConfig(telescopeName):
  telescope = config['telescopes'][telescopeName]
  for key in telescope:
    if isinstance(telescope[key], str) and '$HOME' in telescope[key]:
      telescope[key] = telescope[key].replace('$HOME', str(Path.home()))
  telescope['shortname'] = telescopeName
  return telescope

nodeName = platform.uname().node
if nodeName == config['rootserver']['nodename']:
  telescopes = config['telescopes']
  locations = config['locations']
  rootserver = config['rootserver']
  weatherkit=config['weatherkit']
  logging.info(f"running on rootserver: {nodeName}")
else:
  telescope={}
  if 'telescopes' in config:
    for _telescope in config['telescopes']:
      if 'nodename' in config['telescopes'][_telescope]:
        if config['telescopes'][_telescope]['nodename'] == nodeName:
          logging.info(f"running on telescope: {_telescope}")
          telescope = config['telescopes'][_telescope]
          for key in telescope:
            if isinstance(telescope[key], str) and '$HOME' in telescope[key]:
              telescope[key] = telescope[key].replace('$HOME', str(Path.home()))
          telescope['shortname'] = _telescope
          break
    if telescope=={}:
      logging.error(f"telescope configuration matching node {nodeName} is missing in config.json")
      print(f"telescope configuration matching node {nodeName} is missing in config.json, please fix!")
      sys.exit(1)
  else:
    sys.exit(1)

  #from Common.uploadData import uploadLogFile
  #uploadLogFile()

  if 'locations' in config:
    locations=config['locations']
    if telescope['location'] in config['locations']:
      logging.info(f"telescope location is {telescope['location']}")
      location=config['locations'][telescope['location']]
    else:
      logging.error(f"location configuration for telescope {telescope.shortname} is missing in config.json")
      print(f"location configuration for telescope {telescope.shortname} is missing in config.json, please fix!")
      sys.exit(1)
  else:
    logging.error(f"location configuration is missing in config.json")
    print(f"locations configuration is missing in config.json, please fix!")
    sys.exit(1)

  if 'rootserver' in config:
    rootserver=config['rootserver']
  else:
    logging.error(f"rootserver configuration is missing in config.json")
    print("rootserver configuration is missing in config.json, please fix!")
    sys.exit(1)

  if 'weatherkit' in config:
    weatherkit=config['weatherkit']
  else:
    logging.error(f"weatherkit token configuration is missing in config.json, weather data will not be available")
    print("weatherkit token configuration is missing in config.json, please fix if you want to use weather data!")
    weatherkit={}

  if 'idrive' in config:
    idrive=config['idrive']
  else:
    logging.error("idrive (s3) configuration is missing in config.json, upload to a S3 compatible drive will not be available")
    print("idrive (s3) configuration is missing in config.json, please fix if you want to upload to a S3 compatible drive!")
    idrive={}

  if 'powerboxes' in config and 'powerbox' in telescope:
    if telescope['powerbox'] in config['powerboxes']:
      powerbox=config['powerboxes'][telescope['powerbox']]
    else:
      logging.error(f"powerbox configuration for powerbox {config['powerbox']} is missing in config.json, weather data will not be available")
      print(f"powerbox configuration for powerbox {config['powerbox']} is missing in config.json, please fix if you want to use weather data!")
  else:
    if 'powerbox' in telescope:
      logging.error(f"powerbox is defined for telescope {telescope['shortname']} but no powerboxes found")
      print(f"powerbox is defined for telescope {telescope['shortname']} but no powerboxes found, please fix!")
      raise ValueError(f"powerbox is defined for telescope {telescope['shortname']} but no powerboxes found, please fix!")

