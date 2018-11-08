# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with
the left/right mouse buttons. Right click on any plot to show a context menu.

Overlay Circles and Rectangles
------------------------------

You can add any instances of QGraphicsItem to the view with ViewBox.addItem().
Qt and pyqtgraph both provide a variety of QGraphicsItem subclasses to pick from:

http://qt-project.org/doc/qt-4.8/qgraphicsitem.html#details
http://www.pyqtgraph.org/documentation/graphicsItems/index.html

For simple boxes and lines you can use QGraphicsRectItem, QGraphicsLineItem,  and QGraphicsPathItem.
For more complex shapes (and especially if you want to generate shapes from numpy arrays) you can play with pg.PlotCurveItem and pg.arrayToQPath.

Also see the "isocurve" example.

"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.resize(800,600)
win.show()
win.setWindowTitle('pyqtgraph example: Histogram LUT')

cw = QtGui.QWidget()
win.setCentralWidget(cw)

l = QtGui.QGridLayout()
cw.setLayout(l)
l.setSpacing(0)

v = pg.GraphicsView()
vb = pg.ViewBox()
vb.setAspectLocked()
v.setCentralItem(vb)
l.addWidget(v, 0, 0)

w = pg.HistogramLUTWidget()
l.addWidget(w, 0, 1)

data = pg.gaussianFilter(np.random.normal(size=(256, 256)), (20, 20))
for i in range(32):
    for j in range(32):
        data[i*8, j*8] += .1
img = pg.ImageItem(data)
#data2 = np.zeros((2,) + data.shape + (2,))
#data2[0,:,:,0] = data  ## make non-contiguous array for testing purposes
#img = pg.ImageItem(data2[0,:,:,0])
vb.addItem(img)
vb.autoRange()

w.setImageItem(img)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
