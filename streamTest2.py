import cv2
import gi
import multiprocessing
import asyncio
import time
from pyppeteer import launch

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject
 
class ScreenShotProducer(multiprocessing.Process):

    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        #self.url = 'https://ymlai87416.github.io/hkcovidmap/'
        self.url = 'http://localhost:8080/'
        self.task_queue = task_queue
        

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.screencastSlide(self.url))

    async def screencastSlide(self, url):
        #'headless': False如果想要浏览器隐藏更改False为True
        # 127.0.0.1:1080为代理ip和端口，这个根据自己的本地代理进行更改，如果是vps里或者全局模式可以删除掉'--proxy-server=127.0.0.1:1080'
        browser = await launch({'headless': True, 'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.setViewport({'width': 1280, 'height': 780})
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    
        await page.goto(url, timeout=0)
    
        while True:
            # 'fullPage': True, 
            await page.screenshot({'path': './covid.png', 'quality': 100, 'clip': {'x': 8, 'y': 20, 'width':1280, 'height': 720}})
            data = cv2.imread('./covid.png')
            # slower than the consumer
            self.task_queue.put(data)
            time.sleep(0.2)

 
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, q, **properties):
        super(SensorFactory, self).__init__(**properties)
        # self.cap = cv2.VideoCapture("path/to/video")

        self.number_frames = 0
        self.fps = 10
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width=1280,height=720,framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ! queue ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96 '.format(self.fps)
        # streams to gst-launch-1.0 rtspsrc location=rtsp://localhost:8554/test latency=50 ! decodebin ! autovideosink

        self.queue = q
        self.cur_image = None
 
    def on_need_data(self, src, lenght):
        
        try:
            next_image = self.queue.get(False)
            self.cur_image = next_image
        except: 
            pass

        data = self.cur_image.tostring()
        #print(data)
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp
        self.number_frames += 1
        retval = src.emit('push-buffer', buf)
        #print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
        #                                                                       self.duration,
        #                                                                       self.duration / Gst.SECOND))
        if retval != Gst.FlowReturn.OK:
            print(retval)
 
    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)
 
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)
 
 
class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, q, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory(q)
        self.factory.set_shared(True)
        self.get_mount_points().add_factory("/test", self.factory)
        self.attach(None)
 
def runX():
    q = multiprocessing.Queue()

    producer = ScreenShotProducer(q)
    producer.start()

    GObject.threads_init()
    Gst.init(None)
    
    server = GstServer(q)
    
    loop = GObject.MainLoop()
    loop.run()

if __name__ == '__main__':
    runX()