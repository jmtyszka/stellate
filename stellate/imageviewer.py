#!/usr/bin/env python3
"""
Image viewer subclass of PyQtGraph PlotItem

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-08 JMT Implement using PyQt5 QGraphicsView
2018-11-07 JMT Reimplement using PyQtGraph widget
2019-02-20 JMT Start migration to PySide2 - official bindings for Qt5

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
import pyqtgraph as pg
from skimage.exposure import rescale_intensity
from skimage.color import rgb2hsv, hsv2rgb
# from pyqtgraph.Qt import QtGui, QtWidgets
from stellate.astroimage import AstroImage

class ImageViewer(pg.GraphicsView):
	
	def __init__(self, central_widget):
		
		# Init the base class
		super().__init__()
		
		# Setup PyQtGraph configuration options
		pg.setConfigOption('antialias', True)
		pg.setConfigOption('imageAxisOrder', 'row-major')
		
		self._image_view = pg.ViewBox()
		self._image_view.setAspectLocked(True)
		self.setCentralItem(self._image_view)
		
		# Add image item to image view
		self._image_item = pg.ImageItem()
		self._image_view.addItem(self._image_item)
		
		# Add star tag overlay group
		self._star_tags = QtWidgets.QGraphicsItemGroup()
		self._image_view.addItem(self._star_tags)
		
		# Add empty astroimage
		self._astroimg = AstroImage()
		
		# Init scale settings
		self._scale_settings = 0.0, 100.0
		
		# Finally show the GraphicsView
		self.show()
	
	def set_image(self, astroimg=AstroImage, scale_settings=(0.0, 100.0, True)):
		
		if astroimg.has_image():
			
			self._astroimg = astroimg
			self._has_image = True
			
			# Map scale settings to image intensities
			self._scale_settings = scale_settings
			self.scale_intensities()
			
			# Extract image data from astroimage
			img = self._astroimg.image()
			
			# Rescale image intensities
			img_adj = rescale_intensity(img, in_range=self._ilims, out_range='uint16')
			
			# Replace image data in the ImageItem
			self._image_item.setImage(img_adj, autoDownsample=True)
		
		else:
			
			self._has_image = False
	
	def show_stars(self, stars_df):
		"""
		stars is a list of star region properties [rr, cc, diam, circ]
		- rr, cc : row, col of intensity weighted centroid in image space
		- diam   : equivalent circle diameter
		- circ   : region circularity (1.0 = perfect circle)

		:param stars: Pandas dataframe, star metrics
		:return:
		"""
		
		# Green pen for tags
		pen = QtGui.QPen(QtGui.QColor('#00FF00'), 1)
		
		# Create a group for the tags
		self._star_tags = QtWidgets.QGraphicsItemGroup()
		
		for index, row in stars_df.iterrows():
			
			yc, xc, d, c = row['yc'], row['xc'], row['diam'], row['circ']
			
			# Radius of internal space for cross-hairs
			r = d * 0.75
			
			# Tag above
			tag0 = QtWidgets.QGraphicsLineItem(xc, yc+r, xc, yc+2*r)
			tag0.setPen(pen)
			
			# Tag below
			tag1 = QtWidgets.QGraphicsLineItem(xc, yc-r, xc, yc-2*r)
			tag1.setPen(pen)
			
			# Tag left
			tag2 = QtWidgets.QGraphicsLineItem(xc-r, yc, xc-2*r, yc)
			tag2.setPen(pen)
			
			# Tag right
			tag3 = QtWidgets.QGraphicsLineItem(xc+r, yc, xc+2*r, yc)
			tag3.setPen(pen)
			
			# Add tags to overlay group
			self._star_tags.addToGroup(tag0)
			self._star_tags.addToGroup(tag1)
			self._star_tags.addToGroup(tag2)
			self._star_tags.addToGroup(tag3)
		
		self._image_view.addItem(self._star_tags)
	
	def scale_intensities(self):
		
		smin, smax = self._scale_settings
		imin, imax = self._astroimg.intensity_stats()
		irng = imax - imin
		
		# Scaled intensity limits
		ilims = irng * smin/100.0 + imin, irng * smax/100.0 + imin
		
		self._ilims = ilims
	
	def render_lrgb(self, lrgb_astack):
		
		"""
		Render LRGB short AstroStack as a color image in the viewer
		"""
		
		# LRGB AstroStack should have 4 elements
		if not len(lrgb_astack) == 4:
			return
		
		# Make sure all images in stack are the same dimensions
		# Resample as necessary and return resampled dimensions
		ny, nx = lrgb_astack.enforce_size()
		
		rgb = np.zeros([ny, nx, 3])
		
		rgb[:,:,0] = lrgb_astack.astroimage(1).image()
		rgb[:,:,1] = lrgb_astack.astroimage(2).image()
		rgb[:,:,2] = lrgb_astack.astroimage(3).image()
		
		# Convert to HSV
		hsv = rgb2hsv(rgb)
		
		# Replace V channel with lum
		hsv[:,:,2] = lrgb_astack.astroimage(0).image()
		
		# Convert back to RGB
		rgb = hsv2rgb(hsv)
		
		# Replace image data in the ImageItem
		self._image_item.setImage(rgb, autoDownsample=True)


