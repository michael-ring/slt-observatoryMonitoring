#!/usr/bin/env python3
import sys
import time
import serial
import jsonLogHelper
import win32com.client

sys.path.append('.')
sys.path.append('..')
from Common.config import logger,powerbox


def generateJson():
  json=getPowerBoxStatus()
  alljson=jsonLogHelper.appendToDailyLog('powerboxdata',json)
  return alljson


def getPowerBoxStatus():
  ascomid=powerbox['ascomid']
  powerBoxStatus={}
  try:
    logger.info(f"Connecting to power box via Ascom {ascomid}")
    switch = win32com.client.Dispatch(ascomid)
    switch.Connected = True
  except:
    logger.exception("Failed to connect to power box")
    return {}
  powerBoxStatus['model']=switch.Name
  for switchid in range(switch.MaxSwitch):
    if switch.MaxSwitchValue(switchid) == 1.0:
      powerBoxStatus[switch.GetSwitchName(switchid)]=switch.GetSwitch(switchid)
    if switch.MaxSwitchValue(switchid) == 255.0:
      powerBoxStatus[switch.GetSwitchName(switchid)]=switch.GetSwitchValue(switchid)
  return powerBoxStatus


def initialize():
  ascomid=powerbox['ascomid']
  try:
    switch = win32com.client.Dispatch(ascomid)
    switch.Connected = True
  except:
    logger.exception("Failed to connect to power box")
    return {}
  for code in powerbox['init']:
    print(f"{code}->{powerbox['init'][code]}")
    logger.info(f"Sending {code}->{powerbox['init'][code]}")
    for switchid in range(switch.MaxSwitch):
      if switch.GetSwitchName(switchid).startswith(code):
        if switch.MaxSwitchValue(switchid) == 1.0:
          if powerbox['init'][code] == "On":
            switch.SetSwitch(switchid,True)
          else:
            switch.SetSwitch(switchid,False)
        if switch.MaxSwitchValue(switchid) == 255.0:
          if powerbox['init'][code] == "On":
            switch.SetSwitchValue(switchid,255)
          else:
            switch.SetSwitch(switchid,powerbox['init'][code])

  print(getPowerBoxStatus())


def shutdown():
  ascomid=powerbox['ascomid']
  try:
    switch = win32com.client.Dispatch(ascomid)
    switch.Connected = True
  except:
    logger.exception("Failed to connect to power box")
    return {}
  for code in powerbox['init']:
    print(f"{code}->Off")
    logger.info(f"Sending {code}->Off")
    for switchid in range(switch.MaxSwitch):
      if switch.GetSwitchName(switchid).startswith(code):
        if switch.MaxSwitchValue(switchid) == 1.0:
          switch.SetSwitch(switchid,False)
        if switch.MaxSwitchValue(switchid) == 255.0:
            switch.SetSwitchValue(switchid,0)

  print(getPowerBoxStatus())


if __name__ == '__main__':
  generateJson()