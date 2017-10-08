'''
audio_monitor.py

Reads in live audio from the default microphone and displays a live, updating graph of the raw audio and frequency distribution
'''

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyaudio
import os
import time
import sys

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1600,600)
win.setWindowTitle('Live Audio Monitor')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

CHUNK = 4096
RATE = 44100

p = pyaudio.PyAudio() # start Pyaudio class
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK) # Use default input device

p6 = win.addPlot(title="Raw Audio")
p6.setYRange(-2000,2000)

p7 = win.addPlot(title="Frequency (FFT)")
p7.setLabel('left', "Magnitude")
p7.setLabel('bottom', "Frequency", units='Hz')
p7.setXRange(0,10000)
p7.setYRange(0,100000)


curve_raw = p6.plot(pen=(0,255,0))
curve = p7.plot(pen=(0,255,0))
ptr = 0
def update():
    global curve, curve_raw, data, ptr, p6, p7
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    fft = abs(np.fft.fft(data).real)
    fft = fft[:int(len(fft)/2)]# keep only first half
    freq = np.fft.fftfreq(CHUNK,1/RATE)
    freq = freq[:int(len(freq)/2)] # keep only first half
    curve.setData(freq, fft)
    curve_raw.setData(data)
    if ptr == 0:
        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        p7.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
