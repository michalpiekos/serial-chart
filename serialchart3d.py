CONFIG = {
    "source" : "telnet", # Possible are "telnet" | "serial"
    'telnet_host' : '192.168.1.178',
    'telnet_port' : 23,
    'serial_port' : '/dev/ttyACM0',
    'serial_baudrate' : 115200,
    "separator" : " ", # Separator between variables in source data
    "skip_first" : 5, # How many first lines to skip, e.g. to stabilize
    # Provide names for columns. Number of names must match number of columns in data
    # Currently all variables are treated as float. 
    "columns" : ['magX', 'magY', 'magZ', 'gyroX', 'gyroY', 'gyroZ', 'accX', 'accY', 'accZ'], 
    # Pick 3 columns to plot by index.
    "plot_columns" : [0, 1, 2],
    "grid_spacing" : 200,
    "grid_size" : 2000,
    "grid_show" : False,
    "dot_plot" : True, # Show points in 3d space. Might be ommited if you are interested only in projections
    "plane_projection" : True, # Project data on xy, xz, yz planes additionaly to points in 3d space
    "dot_size" : 20,
    "filename" : "data.csv",
    'print_raw' : True # Print raw data on output as it comes
}


import serial
import telnetlib
import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore


class SerialChart3D(object):
    def __init__(self):
        # self.traces = dict()
        self.app = pg.mkQApp("Serial Chart")
        self.w = gl.GLViewWidget()
        # self.w.opts['distance'] = 40
        self.w.setWindowTitle('Plotting {}'.format(CONFIG['source']))
        self.w.resize(1000,600)
        # self.w.setGeometry(0, 110, 1920, 1080)
        self.w.setCameraPosition(distance=CONFIG['grid_size'] * 2)
        self.w.show()

        ### Create the background grids
        if (CONFIG['grid_show']):
            gx = gl.GLGridItem()
            gx.rotate(90, 0, 1, 0)
            # gx.translate(-5, 0, 0)
            gx.setSize(CONFIG['grid_size'], CONFIG['grid_size'])
            gx.setSpacing(CONFIG['grid_spacing'], CONFIG['grid_spacing'])
            gx.setColor((50,50,50))
            self.w.addItem(gx)
            gy = gl.GLGridItem()
            gy.rotate(90, 1, 0, 0)
            gy.setSize(CONFIG['grid_size'], CONFIG['grid_size'])
            gy.setSpacing(CONFIG['grid_spacing'], CONFIG['grid_spacing'])
            gy.setColor((50,50,50))
            # gy.translate(0, -5, 0)
            self.w.addItem(gy)
            gz = gl.GLGridItem()
            gz.setSize(CONFIG['grid_size'], CONFIG['grid_size'])
            gz.setSpacing(CONFIG['grid_spacing'], CONFIG['grid_spacing'])
            gz.setColor((50,50,50))
            # gz.translate(0, 0, -5)
            self.w.addItem(gz)
        
        ### Create axis
        axisitem = gl.GLAxisItem()
        axisitem.setSize(CONFIG['grid_size'], CONFIG['grid_size'], CONFIG['grid_size'])
        axisitem.setDepthValue(10)
        self.w.addItem(axisitem)

        self._source_setup()

        # Define plots
        if CONFIG['dot_plot']:
            self.sp3 = gl.GLScatterPlotItem(pos=self.trimmedData, color=(1,1,1,.9), size=CONFIG['dot_size'], pxMode=False)
            self.w.addItem(self.sp3)
        if (CONFIG['plane_projection']):
            xy = self.trimmedData.copy()
            xy[:,2] = -3000
            self.sp0 = gl.GLScatterPlotItem(pos=xy, color=(1,1,0,.9), size=CONFIG['dot_size'], pxMode=False)
            xz = self.trimmedData.copy()
            xz[:,1] = -3000
            self.sp1 = gl.GLScatterPlotItem(pos=xz, color=(1,0,0,.9), size=CONFIG['dot_size'], pxMode=False)
            yz = self.trimmedData.copy()
            yz[:, 0] = -3000
            self.sp2 = gl.GLScatterPlotItem(pos=yz, color=(0,1,0,.9), size=CONFIG['dot_size'], pxMode=False)
            self.w.addItem(self.sp0)
            self.w.addItem(self.sp1)
            self.w.addItem(self.sp2)
        

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
        self.trimmedData = self.data[:,CONFIG['plot_columns']].copy()


    def getaslist(self):
        if CONFIG['source'] == 'telnet':
            tmp = self.com.read_until(b"\r\n", 5).decode("ascii").strip().split(CONFIG['separator'])
            if CONFIG['print_raw']:
                print(tmp)
            return tmp
        elif (CONFIG['source'] == 'serial'):
            tmp = str(self.com.readline())[2:-5].split(CONFIG['separator'])
            if CONFIG['print_raw']:
                print(tmp)
            return tmp


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            # QtGui.QApplication.instance().exec_()
            pass

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)

    def update(self):
        try:
            self.data = np.append(self.data, [[float(x) for x in self.getaslist()]], axis=0)
        except:
            return
        self.trimmedData = self.data[:,CONFIG['plot_columns']].copy()
        if CONFIG['dot_plot']:
            self.sp3.setData(pos=self.trimmedData)
        if (CONFIG['plane_projection']):
            xy = self.trimmedData.copy()
            xy[:,2] = -3000
            xz = self.trimmedData.copy()
            xz[:,1] = -3000
            yz = self.trimmedData.copy()
            yz[:, 0] = -3000
            self.sp0.setData(pos=xy)
            self.sp1.setData(pos=xz)
            self.sp2.setData(pos=yz)


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
        # self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    v = SerialChart3D()
    v.animation()
    v.close()
    # v.saveData()
