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

from skimage.exposure import rescale_intensity
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage, QBrush, QPen, QColor
from stellate.starfinder import *


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
        self._scaling_mode = 'linear'
        self._ilims = 0, 1

        # Scene components
        self._scene = QtWidgets.QGraphicsScene(self)
        self._image = QtWidgets.QGraphicsPixmapItem()
        self._mask = QtWidgets.QGraphicsPixmapItem()
        self._staroverlay = QtWidgets.QGraphicsItemGroup()
        self._annotations = QtWidgets.QGraphicsItemGroup()

        # Add items to scene
        self._scene.addItem(self._image)
        self._scene.addItem(self._mask)
        self._scene.addItem(self._staroverlay)
        self._scene.addItem(self._annotations)

        # Add scene behind viewer
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def has_image(self):
        return not self._empty

    def set_image(self, img16=None, reset=False):

        if img16.any():

            self._img16 = img16.copy()
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

            self.image_histogram()

            self.expose_image()

        else:

            # No image in scene
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._image.setPixmap(QPixmap())

        if reset:
            self.fitInView()

    def image_histogram(self):

        # Get histogram widget from main window
        hist_widget = self.parent


    def expose_image(self):

        if self.has_image():

            if 'percentile' in self._scaling_mode:
                ilims = 0.0, np.percentile(self._img16, 95.0)
            else:
                ilims = self._ilims

            # Rescale to uint8
            self._img8 = rescale_intensity(self._img16, in_range=ilims, out_range=(0, 255)).astype(np.uint8)

            # Convert the uint8 grayscale image to a pixmap
            w, h = self._img8.shape[1], self._img8.shape[0]
            img_pixmap = QPixmap(QImage(self._img8, w, h, QImage.Format_Grayscale8))

            # Place image pixmap in scene
            self._image.setPixmap(img_pixmap)

    def show_stars(self, stars):
        """
        Fill star overlay group item with green star bboxes

        :param stars: regionprop object (scikit-image.measure)
        :return:
        """

        for s in stars:

            bb = s.bbox
            x, y = bb[1], bb[0]
            w, h = bb[3]-bb[1], bb[2]-bb[0]

            # Green bbox, width 1
            star_rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
            pen = QPen(QColor('#00FF00'), 1)
            star_rect.setPen(pen)

            # Add bbox to star overlay group
            self._staroverlay.addToGroup(star_rect)

    def set_scaling(self, scaling_mode, ilims):

        self._scaling_mode = scaling_mode
        self._ilims = ilims

        self.expose_image()

    #
    # Override methods
    #

    def fitInView(self, scale=True):

        rect = QtCore.QRectF(self._image.pixmap().rect())

        if not rect.isNull():
            self.setSceneRect(rect)

            if self.has_image():

                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())

                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)

                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())

                self.scale(factor, factor)

            self._zoom = 0

    def wheelEvent(self, event):
        """
        Handle image zoom

        :param event:
        :return:
        """

        if self.has_image():

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

        if self._image.isUnderMouse():
            self.imageClicked.emit(QtCore.QPoint(event.pos()))

        super(imgViewer, self).mousePressEvent(event)

    def keyPressEvent(self, event):

            event.ignore()