#!/usr/bin/env python3
import sys
import serial
import jsonLogHelper
try:
  sys.path.append('.')
  sys.path.append('..')
  from config import telescope
except:
  print("telescope configuration is missing in config.py")
  sys.exit(1)

def generateJson():
  json=getPowerBoxStatus()
  alljson=jsonLogHelper.appendToDailyLog('powerboxdata',json)
  return alljson

def getPowerBoxStatus():
  port=telescope['powerboxstatus'].split(":")[0]
  rate=telescope['powerboxstatus'].split(":")[1]
  powerBoxStatus={}
  try:
    ser = serial.Serial(port, rate, timeout=1)
    data=ser.readline().decode('utf-8')
    if not data.startswith('ZXWBProV3'):
      data = ser.readline().decode('utf-8')
    data=data.split('A')
  except:
    return {}

  powerBoxStatus['model']=data[0]
  powerBoxStatus['firmwareversion']=data[1]
  powerBoxStatus['probe1temperature']=data[2]
  powerBoxStatus['probe2temperature']=data[3]
  powerBoxStatus['probe3temperature']=data[4]
  powerBoxStatus['humidity']=data[5]
  powerBoxStatus['temperature']=data[6]
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
  return powerBoxStatus

if __name__ == '__main__':
  generateJson()