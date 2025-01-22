#!/usr/bin/env python3
import sys
import time
import serial
import jsonLogHelper

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,powerbox


def generateJson():
  json=getPowerBoxStatus()
  alljson=jsonLogHelper.appendToDailyLog('powerboxdata',json)
  return alljson


def getPowerBoxStatus():
  port=powerbox['port']
  speed=powerbox['speed']
  powerBoxStatus={}
  try:
    logger.info(f"Connecting to power box serial {port} {speed}")
    powerBoxStatus['port']=port
    ser = serial.Serial(port, speed, timeout=1)
    data=ser.readline().decode('utf-8')
    if not data.startswith(powerbox['identifier']):
      data = ser.readline().decode('utf-8')
    logger.info(f"Initial serial data: {data}")
    data=data.split('A')
  except:
    logger.exception("Failed to connect to power box")
    return {}
  ser.close()
  if len(data) >= 22:
    logger.info(f"complete dataset found")
    powerBoxStatus['model']=data[0]
    powerBoxStatus['firmwareversion']=data[1]
    powerBoxStatus['probe1temperature']=data[2]
    powerBoxStatus['probe2temperature']=data[3]
    powerBoxStatus['probe3temperature']=data[4]
    powerBoxStatus['humidity']=data[5]
    powerBoxStatus['temperature']=data[6]
    powerBoxStatus['dewpoint']=f"{float(data[6])-((100-float(data[5]))/5):.2f}"
    powerBoxStatus['inputcurrent']=data[7]
    powerBoxStatus['output19vcurrent']=data[8]
    powerBoxStatus['adjustableoutputcurrent']=data[9]
    powerBoxStatus['inputvoltage']=data[10]
    powerBoxStatus['usb31status']=data[11]
    powerBoxStatus['usb32status']=data[12]
    powerBoxStatus['usb33status']=data[13]
    powerBoxStatus['usb213status']=data[14]
    powerBoxStatus['usb246status']=data[15]
    powerBoxStatus['dc34status']=data[16]
    powerBoxStatus['dc5status']=data[17]
    powerBoxStatus['dc6status']=data[18]
    powerBoxStatus['dc7status']=data[19]
    powerBoxStatus['dc89status']=data[20]
    powerBoxStatus['dc10']=data[21]
    powerBoxStatus['dc34voltage']=int(data[22])/10
  else:
    logger.error("incomplete dataset found")
  return powerBoxStatus


def initialize():
  port=powerbox['port']
  speed=powerbox['speed']
  try:
    logger.info(f"Connecting to power box serial {port} {speed}")
    ser = serial.Serial(port, speed, timeout=1)
    data=ser.readline().decode('utf-8')
    print(data)
    if not data.startswith(powerbox['identifier']):
      data = ser.readline().decode('utf-8')
    logger.info(f"Initial serial data: {data}")
  except:
    print('Exception, is Serial Port connected?')
    logger.exception("Failed to connect to power box")
    return {}
  for code in powerbox['init']:
    logger.info(f"Sending code {code}")
    print(f"Init Code: {code}")
    ser.write((str(code)+'\r\n').encode())
    time.sleep(1)
    data=ser.readline().decode('utf-8')
    time.sleep(1)
    data=ser.readline().decode('utf-8')
  ser.close()
  print(getPowerBoxStatus())


def shutdown():
  port=powerbox['port']
  speed=powerbox['speed']
  try:
    ser = serial.Serial(port, speed, timeout=1)
    data=ser.readline().decode('utf-8')
    print(data)
    if not data.startswith(powerbox['identifier']):
      data = ser.readline().decode('utf-8')
  except:
    print('Exception, is Serial Port connected?')
    return {}
  for code in powerbox['shutdown']:
    print(f"Shutdown Code: {code}")
    ser.write((str(code)+'\r\n').encode())
    time.sleep(1)
    data=ser.readline().decode('utf-8')
    time.sleep(1)
    data=ser.readline().decode('utf-8')
  ser.close()
  print(getPowerBoxStatus())


if __name__ == '__main__':
  generateJson()