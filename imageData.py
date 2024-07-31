#!/usr/bin/env python3
from fits2image import conversions
import boto3
import sys

conversions.fits_to_jpg("/Users/tgdrimi9/Desktop/2024-07-28/Crescent Nebula/SkyEye24AC_Askar ACL200_HaOiii_158_300.00_2024-07-29_03-47-44_-0.10°C.fits",
                       "/Users/tgdrimi9/Desktop/test.jpg",width=2000,height=2000)

try:
  from config import idrive
except:
  print("idrive configuration is missing in config.py")
  sys.exit(1)

client = boto3.client("s3", endpoint_url=idrive['endpoint'], aws_access_key_id=idrive['accessKeyId'], aws_secret_access_key=idrive['secretAccessKey'])

objects = client.list_objects(Bucket=idrive['bucket'],Prefix="previews/")
print(objects)