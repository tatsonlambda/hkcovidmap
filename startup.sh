pushd /home/ymlai/hkcovidmap/slide

# run the web in background
npm run serve &

popd

pushd /home/ymlai/hkcovidmap

# run the stream in background

python3 streamTest2.py &

./youtube.sh &

popd