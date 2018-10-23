#!/usr/bin/env python3
"""
Image viewer subclass of QtWidgets.QGraphicsView
- implements mouse pan/zoom

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-08 JMT Adapt from example SO code at
    https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
    Credit: ekhumoro

LICENSE
----

This file is part of Stellate.

Stellate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Stellate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with stellate.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from skimage.exposure import rescale_intensity
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QPen, QBrush, QColor


class imgViewer(QtWidgets.QGraphicsView):
    """
    Image viewer subclass of QGraphicsView
    """

    imageClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, centralWidget):

        # Init the base class
        super().__init__()

        # Internal variables
        self._zoom = 0
        self._empty = True
        self._autostretch = False
        self._scene = QtWidgets.QGraphicsScene(self)
        self._image = QtWidgets.QGraphicsPixmapItem()
        self._stars = QtWidgets.QGraphicsItemGroup()

        # Populate scene with placeholder items
        self._scene.addItem(self._image)
        self._scene.addItem(self._stars)

        # Add scene behind viewer
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasImage(self):
        return not self._empty

    def fitInView(self, scale=True):

        rect = QtCore.QRectF(self._image.pixmap().rect())

        if not rect.isNull():
            self.setSceneRect(rect)

            if self.hasImage():

                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())

                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)

                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())

                self.scale(factor, factor)

            self._zoom = 0

    def setImage(self, img16=None):

        # Add non-empty image to scene

        self._zoom = 0

        if img16.any():

            self._img16 = img16.copy()
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.exposeImage()

        else:

            # No image in scene
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._image.setPixmap(QPixmap())

        self.fitInView()

    def exposeImage(self):

        # Reveal image scene within viewer

        if self.hasImage():

            if self._autostretch:
                ilims = 0.0, np.percentile(self._img16, 95.0)
            else:
                ilims = 0.0, np.max(self._img16)

            # Rescale to uint8
            self._img8 = rescale_intensity(self._img16, in_range=ilims, out_range=(0, 255)).astype(np.uint8)

            # Convert the uint8 grayscale image to a pixmap
            w, h = self._img8.shape[1], self._img8.shape[0]
            pixmap = QPixmap(QImage(self._img8, w, h, QImage.Format_Grayscale8))

            # Finally place pixmap in scene
            self._image.setPixmap(pixmap)

            # Add green circle to scene
            starPen = QPen(QColor("#00FF00"))
            starBrush = QBrush(QColor("#00FF00"))
            self._scene.addEllipse(100, 100, 80, 40, starPen)


    def wheelEvent(self, event):
        """
        Handle image zoom

        :param event:
        :return:
        """

        if self.hasImage():

            dphi = event.angleDelta().y()

            if dphi > 0:
                factor = 1.1
                self._zoom += 1
            elif dphi < 0:
                factor = 0.9
                self._zoom -= 1
            else:
                factor = 1.0

            if self._zoom > 0:
                self.scale(factor, factor)
            else:
                self._zoom = 0
                self.fitInView()  # Clamp zoom at full window

    def mousePressEvent(self, event):
        # Intercept mouse click even if over image
        if self._image.isUnderMouse():
            self.imageClicked.emit(QtCore.QPoint(event.pos()))
        # Pass mouse click event
        super(imgViewer, self).mousePressEvent(event)

    def autostretch(self, status):
        # Set autostretch status of viewer
        self._autostretch = status
        self.exposeImage()
