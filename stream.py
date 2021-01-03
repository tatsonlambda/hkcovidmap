import asyncio
import time
from pyppeteer import launch
 
#for setup a rtsp server
# https://stackoverflow.com/questions/60571501/how-to-rtsp-stream-a-video-using-gstreamer-and-python
# https://stackoverflow.com/questions/47396372/write-opencv-frames-into-gstreamer-rtsp-server-pipeline


async def screencastSlide(url):
    #'headless': False如果想要浏览器隐藏更改False为True
    # 127.0.0.1:1080为代理ip和端口，这个根据自己的本地代理进行更改，如果是vps里或者全局模式可以删除掉'--proxy-server=127.0.0.1:1080'
    browser = await launch({'headless': True, 'args': ['--no-sandbox']})
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 780})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
 
    await page.goto(url, timeout=0)
 
    while True:
        await page.screenshot({'path': './covid.png', 'quality': 100, 'fullPage': True})
        time.sleep(0.3)
 
if __name__ == '__main__':
    #url = 'https://ymlai87416.github.io/hkcovidmap/'
    url = 'http://localhost:8080/'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(screencastSlide(url))
 