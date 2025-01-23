#!/bin/sh
cd $HOME/devel/slt-observatoryMonitoring/
FILENAME=/home/sltupload/slt-images/allsky-$(TZ=America/Chicago date '+%Y%m%d_%H%M').jpg
wget "https://zyssufjepmbhqznfuwcw.supabase.co/storage/v1/object/public/status-assets-public/building-0009/allsky/images/image.jpg" -q -O $FILENAME
convert $FILENAME -sigmoidal-contrast 15,0% $FILENAME

for file in /home/sltupload/slt-images/allsky-[0-9]*[0-9].jpg ; do
  thumb=$(echo $file | sed "s,.jpg,.thumb.jpg,g")
  vstfile=$(echo $file | sed "s,slt-,vst-,g")
  vstthumb=$(echo $thumb | sed "s,slt-,vst-,g")
  [ ! -f $thumb ] && convert $file -resize 171x171 $thumb
  [ ! -f $vstfile ] && cp $file $vstfile
  [ ! -f $vstthumb ] && cp $thumb $vstthumb
done

. ./venv/bin/activate
python3 Server/weatherStatus.py
python3 Server/telescopePage.py
python3 Server/patchhtml.py