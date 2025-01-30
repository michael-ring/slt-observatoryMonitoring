import datetime
import platform
from pathlib import Path
import json
import sys
import logging.config
import logging.handlers as handlers

loggingFile=Path(__file__).parent.parent / "monitoring.log"

logger = logging.getLogger(__name__)
#logHandler = handlers.TimedRotatingFileHandler(loggingFile, atTime=datetime.time.fromisoformat("12:00:00"), when='D',backupCount=3,encoding="utf-8")
logHandler = handlers.RotatingFileHandler(loggingFile, maxBytes=5000000,backupCount=3,encoding="utf-8")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s")
logHandler.setFormatter(formatter)
logHandler.setLevel(logging.INFO)
logging.basicConfig(handlers=[logHandler],level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.ERROR)
logger.addHandler(console_handler)

def handle_exception(exc_type, exc_value, exc_traceback):
  if issubclass(exc_type, KeyboardInterrupt):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    return
  logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
  print(sys.exc_info())

sys.excepthook = handle_exception

configFile=Path(__file__).parent.parent / "config.json"
if not configFile.is_file():
  logger.error("config.json file not found in main folder")
  raise SystemExit(1)

try:
  config=json.load(configFile.open())
except json.decoder.JSONDecodeError as e:
  print("config.json has parsing errors, please fix!")
  logger.exception(e)
  raise


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

if not 'rootserver' in config:
  logging.error(f"rootserver configuration is missing in config.json")
  raise SystemExit(1)

if not 'locations' in config:
  logging.error(f"locations configuration is missing in config.json")
  raise SystemExit(1)

if not 'telescopes' in config:
  logging.error(f"telescopes configuration is missing in config.json")
  raise SystemExit(1)

if nodeName == config['rootserver']['nodename']:
  telescopes = config['telescopes']
  locations = config['locations']
  rootserver = config['rootserver']
  if not 'weatherkit' in config:
    logging.error(f"weatherkit configuration is missing in config.json")
    raise SystemExit(1)
  weatherkit=config['weatherkit']
else:
  telescope={}
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
    raise SystemExit(1)

  locations=config['locations']
  if telescope['location'] in config['locations']:
    logging.info(f"telescope location is {telescope['location']}")
    location=config['locations'][telescope['location']]
  else:
    logging.error(f"location configuration for telescope {telescope.shortname} is missing in config.json")
    raise SystemExit(1)

  rootserver=config['rootserver']

  if 'idrive' in config:
    idrive=config['idrive']
  else:
    logging.warning("idrive (s3) configuration is missing in config.json, upload to a S3 compatible drive will not be available")
    idrive={}

  if 'powerboxes' in config and 'powerbox' in telescope:
    if telescope['powerbox'] in config['powerboxes']:
      powerbox=config['powerboxes'][telescope['powerbox']]
    else:
      logging.warning(f"powerbox configuration for powerbox {config['powerbox']} is missing in config.json, data will not be available")
  else:
    if 'powerbox' in telescope:
      logging.error(f"powerbox is defined for telescope {telescope['shortname']} but no powerboxes found")
      raise SystemExit(1)
