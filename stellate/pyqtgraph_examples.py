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

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

x2 = np.linspace(-100, 100, 1000)
data = np.sin(x2) / x2

p1 = win.addPlot(title="Region Selection")
p1.plot(data, pen=(255, 255, 255, 200))

# Add linear region selector to p1
lr = pg.LinearRegionItem([400,700])
lr.setZValue(-10)  # region selector drawn behind graph
p1.addItem(lr)

p2 = win.addPlot(title="Zoom on selected region")
p2.plot(data, fillLevel=0.0, brush=(50, 50, 200, 100))
p2.showAxis('left', False)

# Callback functions
def updatePlot():
    p2.setXRange(*lr.getRegion(), padding=0)

def updateRegion():
    lr.setRegion(p2.getViewBox().viewRange()[0])

# If region changed in p1, update p2 x-axis
lr.sigRegionChanged.connect(updatePlot)

# If x-axis changed in p2, update region in p1
p2.sigXRangeChanged.connect(updateRegion)

updatePlot()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
