'''
audio_spectrum.py

Reads in a .wav audio file as a command line argument, and generates an audio spectrum of the file's audio.

>python audio_spectrum.py audi_file.wav

'''

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyaudio
import os
import time
import sys
import wave

app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(1400,800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('Audio Spectrum')


CHUNK = 4096
RATE = 44100
if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio() # start Pyaudio class

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)
data_np = np.fromstring(data, dtype=np.int16)
fft = abs(np.fft.fft(data_np).real)
fft = fft[:int(len(fft)/2)]# keep only first half
#freq = np.fft.fftfreq(CHUNK,1/RATE)
#freq = freq[:int(len(freq)/2)] # keep only first half

ptr = 0
data_full = np.zeros((1, int(len(fft)/3)))
data_full[0]=fft[:int(len(fft)/3)]

# for i in range(int(5*44100/1024)):
#     data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
#     fft = abs(np.fft.fft(data).real)
#     fft = fft[:int(len(fft)/2)]# keep only first half
#     freq = np.fft.fftfreq(CHUNK,1/RATE)
#     freq = freq[:int(len(freq)/2)] # keep only first half
#
#     data_full[i] = fft
#     print(i, int(5*44100/1024))
#
while data != '':
    #stream.write(data)
    data = wf.readframes(CHUNK)
    data_np = np.fromstring(data, dtype=np.int16)
    try:
        fft = abs(np.fft.fft(data_np).real)
        fft = fft[:int(len(fft)/2)]# keep only first half
        data_full = np.append(data_full, [fft[:int(len(fft)/3)]], axis=0)
    except ValueError:
        print("Done.")
        data=''

print(np.argmax(data_full[0]))
data_full = np.flip(data_full, 1)

imv.autoLevels()
imv.setImage(np.sqrt(data_full))
#imv.setImage(np.log(data_full))


# def update():
#     global curve, data, ptr, p6
#     data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
#     fft = abs(np.fft.fft(data).real)
#     fft = fft[:int(len(fft)/2)]# keep only first half
#     freq = np.fft.fftfreq(CHUNK,1/RATE)
#     freq = freq[:int(len(freq)/2)] # keep only first half
#     data_full[ptr] = fft
#     imv.setImage(data_full)
#     #curve.setData(fft)
#     #if ptr == 0:
#     #    p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
#     ptr += 1


## Set a custom color map
colors = [
    (0, 0, 0),
    (45, 5, 61),
    (84, 42, 55),
    (150, 87, 60),
    (208, 171, 141),
    (255, 255, 255)
]

cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
imv.setColorMap(cmap)

# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
