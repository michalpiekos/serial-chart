serial-chart
============
Real time visualize data from serial port or telnet. 2D line charts can have subplots as on below snapshot<br>
![screenshot](/res/screen1.png) <br>
3D scatter plots support projections on 3 planes. Useful for IMU calibration data.
![screenshot](/res/screen2.png)

Installation Method
-------------------

* Requirements
  * Worth to refresh to latest:<br>
  `pip install -U pyqtgraph pyside pyside6 qt5-wayland PyOpenGL PyOpenGL_accelerate`
  * Some issue might arise with `attrs` package. If there are some errors regarding this package I did:<br>
  `pip uninstall attr`<br>
  `pip install attrs`
* Installation<br>
Copy to your project. 

Examples
--------

Run directly or instantiate a class.<br>
```
v = SerialChart2D()
v.animation()
v.close()
v.saveData()
```


