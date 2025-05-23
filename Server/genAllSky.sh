#!/bin/sh
cd $HOME/devel/slt-observatoryMonitoring/

date '+%M' | grep "5$" >/dev/null
GENVIDEO=$?
FILENAME=/home/sltupload/starfront-allsky/allsky-$(TZ=America/Chicago date '+%Y%m%d_%H%M').jpg
wget "https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0009/allsky/images/image.jpg" -q -O $FILENAME
if [ -s $FILENAME ]; then
  convert $FILENAME -sigmoidal-contrast 5,0% $FILENAME
else
  rm -f $FILENAME
fi

if [ -f $FILENAME ]; then
    thumb=$(echo $FILENAME | sed "s,.jpg,.thumb.jpg,g")
    convert $FILENAME -resize 171x171 $thumb
fi

FILENAME=/home/sltupload/deepskychile-allsky/allsky-$(TZ=America/Santiago date '+%Y%m%d_%H%M').jpg
wget "https://weather.deepskychile.com/cameras/ImageLastFTP_AllSKY_lowres.jpg" -q -O $FILENAME
if [ -s $FILENAME ]; then
  #convert $FILENAME -sigmoidal-contrast 5,0% $FILENAME
  echo ""
else
  rm -f $FILENAME
fi

if [ -f $FILENAME ]; then
    thumb=$(echo $FILENAME | sed "s,.jpg,.thumb.jpg,g")
    convert $FILENAME -resize 171x171 $thumb
fi

if [ "$GENVIDEO" = "0" ]; then
  . ./venv/bin/activate 
  python3 Server/allSkyStatus.py
fi
