#! /bin/bash

hour=$(date +%H)
yesterday=$(date -d "yesterday" '+%Y%m%d')
today=$(date +'%Y%m%d')

pushd /home/ymlai/hkcovidmap

if [ "$hour" -lt 8 -a "$hour" -ge 0 ]; then
    echo "execute yesterday batch"
    python3  /home/ymlai/hkcovidmap/batch.py $yesterday
elif [ "$hour" -lt 24 -a "$hour" -ge 11 ]; then
    echo "execute today batch"
    python3  /home/ymlai/hkcovidmap/batch.py $today
else
    echo "skip, data not ready"
fi

popd
