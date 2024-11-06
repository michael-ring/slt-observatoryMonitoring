#!/usr/bin/env python3
import pydevd_pycharm
pydevd_pycharm.settrace('192.168.1.138', port=9999, stdoutToServer=True, stderrToServer=True)
import serial
ser = serial.Serial('COM4',19200,timeout=1)
line = ser.readline()
if line.startswith(b'ZXWBProV3'):
  Fields=line.split(b'A')
  firmware=Fields[1]
  temp1=Fields[2]
  temp2=Fields[3]
  temp3=Fields[4]
  humidity=Fields[5]
  temperature=Fields[6]
  inputCurrent=Fields[7]
  output19Vcurrent=Fields[8]
  outputAdjustableCurrent=Fields[9]
  inputVoltage=Fields[10]
  usb3_1Status=Fields[11]
  usb3_2Status = Fields[12]
  usb3_3Status = Fields[13]
  usb2_13Status = Fields[14]
  usb2_46Status = Fields[15]
  dc34Status = Fields[16]
  dc5Status = Fields[17]
  dc6Status = Fields[18]
  dc7Status = Fields[19]
  dc89Status = Fields[20]
  dc1011Status = Fields[21]
  dc34voltage = Fields[22]
  pass
print(line)