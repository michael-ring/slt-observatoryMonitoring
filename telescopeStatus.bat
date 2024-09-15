cd "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\"
call  "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\venv\Scripts\activate.bat"
set PYTHONPATH=%PYTHONPATH%;"%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\"
mkdir "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\Temp" 2>NUL
python.exe  "%HOMEDRIVE%%HOMEPATH%\devel\slt-observatoryMonitoring\Client\telescopeStatus.py"