#!/bin/sh
cd $HOME/devel/slt-observatoryMonitoring/
. ./venv/bin/activate
python3 Server/weatherStatus.py
date
python3 Server/telescopePage.py
date
python3 Server/patchhtml.py
date
