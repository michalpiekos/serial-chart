CONFIG = {
    "source" : "telnet", # Possible are "telnet" | "serial"
    'telnet_host' : '192.168.1.178',
    'telnet_port' : 23,
    'serial_port' : '/dev/ttyACM0',
    'serial_baudrate' : 115200,
    "separator" : " ", # Separator between variables in source data
    "skip_first" : 5, # How many first lines to skip, e.g. to stabilize
    "window" : 200, # Size of window of data shown on chart
    # Provide names for columns. Number of names must match number of columns in data
    # Currently all variables are treated as float. 
    "columns" : ['magX', 'magY', 'magZ', 'gyroX', 'gyroY', 'gyroZ', 'accX', 'accY', 'accZ'], 
    # Select index of the columns to plot. If nested array then rows represent plots and columns lines.
    "plots" : [[0, 1, 2], [3, 4, 5], [6, 7, 8]], 
    "filename" : "IMU2d.csv",
    'print_raw' : True # Print raw data on output as it comes
}


import serial
import telnetlib
import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


class SerialChart2D(object):
    def __init__(self) -> None:
        self.app = pg.mkQApp("Serial Chart")
        self.w = pg.GraphicsLayoutWidget(show=True, title="2D charts")
        self.w.resize(1200,700)
        self.w.setWindowTitle('Plotting {}'.format(CONFIG['source']))
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        self._source_setup()
        self.plots = []
        self.curves = []
        self.ptr = 0
        for i, row in enumerate(CONFIG['plots']):
            if (i > 0):
                self.w.nextRow()
            plot = self.w.addPlot() # title="Plot {}".format(row)
            plot.addLegend()
            for j, col in enumerate(row):
                self.curves.append(plot.plot(pen=pg.intColor(j), name=CONFIG['columns'][col]))
                print(pg.intColor(j))
            self.plots.append(plot)

    
    def _source_setup(self):
        if CONFIG['source'] == 'telnet':
            self.com = telnetlib.Telnet()
            self.com.open(CONFIG['telnet_host'], CONFIG['telnet_port'])
        elif (CONFIG['source'] == 'serial'):
            self.com = serial.Serial(CONFIG['serial_port'], baudrate=CONFIG['serial_baudrate'], timeout=1)
            self.com.flush()
        else:
            print("Source data is not defined in 'config.py'")
        ### Skip first n datapoints
        for i in range(CONFIG['skip_first']):
            self.getaslist()
        ### Download first line
        line = self.getaslist()
        self.data = np.array([[float(x) for x in line]])


    def getaslist(self):
        if CONFIG['source'] == 'telnet':
            tmp = self.com.read_until(b"\n", 5).decode("ascii").strip().split(CONFIG['separator'])
            if CONFIG['print_raw']:
                print(tmp)
            return tmp
        elif (CONFIG['source'] == 'serial'):
            tmp = str(self.com.readline())[2:-5].split(CONFIG['separator'])
            if CONFIG['print_raw']:
                print(tmp)
            return tmp


    def update(self):
        try:
            self.data = np.append(self.data, [[float(x) for x in self.getaslist()]], axis=0)
        except:
            return
        for i, row in enumerate(CONFIG['plots']):
            for j, col in enumerate(row):
                if self.ptr <= CONFIG['window']:
                    self.curves[(i * len(row)) + j].setData(self.data[:,col])
                elif self.ptr > CONFIG['window']:
                    self.curves[(i * len(row)) + j].setData(self.data[-CONFIG['window']:,col])
                    self.curves[(i * len(row)) + j].setPos(self.ptr - CONFIG['window'], 0) # - CONFIG['window']
                    
        self.ptr += 1

    def saveData(self, fn=CONFIG['filename']):
        df = pd.DataFrame(self.data, columns=CONFIG['columns'])
        df.to_csv(fn, index=False)
    

    def close(self):
        self.com.close()
        print("Closed connections")
            

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        pg.exec()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = SerialChart2D()
    v.animation()
    v.close()
    v.saveData()