C:
cd "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\"
call  "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\venv\Scripts\activate.bat"
set PYTHONPATH=%PYTHONPATH%;"%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\"
python.exe  "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\Client\powerBoxInitialize.py"
pause
