# -*- coding: utf-8 -*-


from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
import pyaudio
import wave
import sys
import warnings
from time import gmtime, strftime, localtime

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)



def record_dark():

    CHUNK = 4096
    RATE = 44100

    p = pyaudio.PyAudio() # start Pyaudio class
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK) # Use default input device

    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    data_np = np.fromstring(data, dtype=np.int16)
    fft = abs(np.fft.fft(data_np).real)
    fft = fft[:int(len(fft)/2)]# keep only first half
    #freq = np.fft.fftfreq(CHUNK,1/RATE)
    #freq = freq[:int(len(freq)/2)] # keep only first half

    data_full = np.zeros((1, int(len(fft)/3)))
    data_full[0]=fft[:int(len(fft)/3)]

    print("RECORDING DARK AUDIO - REMAIN SILENT...")

    i = 0
    while data != '' and i <=1000:
        print(str(i) + " out of 1000", end="\r", flush=True)
        data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
        data_np = np.fromstring(data, dtype=np.int16)
        try:
            fft = abs(np.fft.fft(data_np).real)
            fft = fft[:int(len(fft)/2)]# keep only first half
            data_full = np.append(data_full, [fft[:int(len(fft)/3)]], axis=0)
            i+=1
        except ValueError:
            data=''

    average_data = np.mean(data_full, axis=0)
    return average_data

app = QtGui.QApplication([])

## Create window with GraphicsView widget
win = pg.GraphicsLayoutWidget()

win.move(-1200,1200)
#win.move(2500,600)
#win.show()  ## show widget alone in its own window
win.showFullScreen()

win.setWindowTitle('Live Audio Spectrum')

img = pg.ImageItem()

'''
p1 = win.addPlot()

p1.setAspectLocked(True)
p1.hideAxis('bottom')

#p1.setYRange(0, 12000)

p1.addItem(img)
'''

#'''
view = win.addViewBox()
view.addItem(img)
## lock the aspect ratio so pixels are always square
view.setAspectLocked(True)
#'''

# Set Color

'''
lut = np.zeros((255,3), dtype=np.ubyte)
lut[:128,0] = np.arange(0,255,2)
lut[128:,0] = 255
lut[:,1] = np.arange(255)
'''

red = np.zeros((255,3), dtype=np.ubyte)
red[:128,0] = np.arange(0,255,2)
red[128:,0] = 255
red[:,1] = np.arange(255)

green = np.zeros((255,3), dtype=np.ubyte)
green[:128,1] = np.arange(0,255,2)
green[128:,1] = 255
green[:,2] = np.arange(255)

blue = np.zeros((255,3), dtype=np.ubyte)
blue[:128,2] = np.arange(0,255,2)
blue[128:,2] = 255
blue[:,1] = np.arange(255)

purple = np.zeros((255,3), dtype=np.ubyte)
purple[:128,2] = np.arange(0,255,2)
purple[128:,2] = 255
purple[:,0] = np.arange(255)

other = np.zeros((255,3), dtype=np.ubyte)
other[:128,0] = np.arange(0,255,2)
other[128:,0] = 255
other[:,2] = np.arange(255)

lut = blue


img.setLookupTable(lut)
#img.setLevels([[0, 50000], [0, 1], [0, 1]], update=True)

CHUNK = 4096
RATE = 44100

p = pyaudio.PyAudio() # start Pyaudio class
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK) # Use default input device

#data = wf.readframes(CHUNK)
data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
data_np = np.fromstring(data, dtype=np.int16)
fft = abs(np.fft.fft(data_np).real)
fft = fft[:int(len(fft)/2)]# keep only first half
freq = np.fft.fftfreq(CHUNK,1/RATE)
freq = freq[:int(len(freq)/2)] # keep only first half

if len(sys.argv) > 1 and sys.argv[1] == 'dark':
    #dark_frame = record_dark()
    dark_frame = np.load('dark_frame.npy')
    dark_string = "_dark_subtracted"
else:
    dark_frame = np.zeros((1, int(len(fft)/3)))
    dark_string = ""

print("Mean Dark Level: ", np.mean(dark_frame))

ptr = 0
data_full = np.zeros((1, int(len(fft)/3)))
data_full[0]=fft[:int(len(fft)/3)] - dark_frame

## Set initial view bounds
view.setRange(QtCore.QRectF(0, 0, 1000, data_full.shape[1]))#**********************
#p1.setRange(QtCore.QRectF(0, 0, 1000, data_full.shape[1]))
#p1.setRange(QtCore.QRectF(0, 0, 1000, int(freq[len(freq)/3])))


i = 0

updateTime = ptime.time()
fps = 0
#print("N Elements = ", len(fft)/3)

def updateData():
    global img, data, data_full, i, updateTime, fps, filename
    if data != '':
        #stream.write(data)
        #data = wf.readframes(CHUNK)
        data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
        data_np = np.fromstring(data, dtype=np.int16)
        try:
            fft = abs(np.fft.fft(data_np).real)
            fft = fft[:int(len(fft)/2)]# keep only first half
            if i == 0:
                start_time = strftime("%d-%b-%Y_%H-%M-%S", localtime())
                filename = "C:\\Users\\samue\\Documents\\Python Scripts\\audio_spectra\\" + start_time + dark_string + ".tif"
            if i > 1000:
                img.save(filename)
                #img.save("test_image_blah.tif")
                print("Saved " + filename)
                data_full = np.zeros((1, int(len(fft)/3)))
                data_full[0]=fft[:int(len(fft)/3)] - dark_frame
                i=0
            else:
                data_full = np.append(data_full, [fft[:int(len(fft)/3)]] - dark_frame, axis=0)
                i+=1
        except ValueError:
            print("Done.")
            data=''

    ## Display the data
    #img.border = None
    #img.setImage(data_full, levels=(0,50000))
    img.setImage(data_full, levels=(0,100000))
    #img.setImage(np.sqrt(data_full), levels=(0,np.sqrt(50000)))
    #img.setImage(np.log(data_full), levels=(1,np.log(50000)))
    #img.levels(0,100000)
    #i = (i+1) % data.shape[0]

    QtCore.QTimer.singleShot(1, updateData)
    now = ptime.time()
    fps2 = 1.0 / (now-updateTime)
    updateTime = now
    fps = fps * 0.9 + fps2 * 0.1

    #print("%0.1f fps" % fps)


updateData()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
