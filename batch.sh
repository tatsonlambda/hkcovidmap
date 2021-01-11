#! /bin/bash

pushd /home/ymlai/hkcovidmap

python3  /home/ymlai/hkcovidmap/batch.py $(date +'%Y%m%d')

popd
