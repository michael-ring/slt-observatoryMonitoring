#!/bin/sh
cd $HOME/devel/slt-observatoryMonitoring/
. ./venv/bin/activate
python3 Server/weatherStatus.py
