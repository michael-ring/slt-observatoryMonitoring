#!/usr/bin/env python3
import sys
import datetime
import PIL.Image
from pathlib import Path

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,telescopes, locations, rootserver,runningOnServer
from Common import locationData

def getAllSkyFrames(telescopeName,overrideDateTime=None,startTime=None,endTime=None):
  if runningOnServer():
    allSkyFiles=list((Path(rootserver['uploadsdir']) / f"{telescopeName}-images").glob("allsky-*[0-9].jpg"))
  else:
    allSkyFiles=list((Path(rootserver['uploadsdir']) / f"{telescopeName}-images").glob("allsky-*[0-9].jpg"))
  logger.info(f"{len(allSkyFiles)} allsky frames found for {telescopeName}")
  if startTime==None or endTime==None:
    sunStatus=locationData.getSunData(locations[telescopes[telescopeName]['location']],overrideDateTime)
    if sunStatus['alt'] >=-6:
      startTime=sunStatus['previoustwilightset']
      endTime=sunStatus['previoustwilightrise']
    else:
      startTime=sunStatus['previoustwilightset']
      endTime=sunStatus['nexttwilightrise']

  activeFiles={}
  for allSkyFile in allSkyFiles:
    fileDate=datetime.datetime.strptime(allSkyFile.name, 'allsky-%Y%m%d_%H%M.jpg').replace(tzinfo=startTime.tzinfo)
    if fileDate >= startTime and fileDate <= endTime:
      activeFiles[fileDate]=allSkyFile
  activeFiles=dict(sorted(activeFiles.items()))
  logger.info(f"{len(activeFiles)} allsky frames matching {startTime} to {endTime} found for {telescopeName}")
  return activeFiles

def renderVideo(telescopeName):
  activeFiles=getAllSkyFrames(telescopeName)
  if len(activeFiles)>1:
    firstImg=Path(next(iter(activeFiles.values())))
    imgSize=PIL.Image.open(firstImg).size
    imgRatio=imgSize[0]/imgSize[1]
    outputMovie=firstImg.with_name('allsky.webp')
    outputThumbMovie=firstImg.with_name('allsky-thumb.webp')
    frames=[]
    for key,img in activeFiles.items():
      try:
        frames.append(PIL.Image.open(img).resize((1200,int(1200*imgRatio))))
      except:
        logger.exception(f"Could not load/render file {img}, ignoring")
        pass
    frames[0].save(outputMovie, "webp", save_all=True, append_images=frames[1:],duration=10)
    logger.info(f"Rendered allsky video {outputMovie.name}")
    frames=[]
    for key,img in activeFiles.items():
      try:
        frames.append(PIL.Image.open(img).resize((360,int(360*imgRatio))))
      except:
        logger.exception(f"Could not load/render file {img}, ignoring")
        pass
    frames[0].save(outputThumbMovie, "webp", save_all=True, append_images=frames[1:],duration=10)
    logger.info(f"Rendered allsky video {outputThumbMovie.name}")
  else:
    logger.error(f"Not enough frames found for telescope {telescopeName}, not rendering video")
if __name__ == '__main__':
  renderVideo('slt')


