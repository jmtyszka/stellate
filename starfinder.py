#!/usr/bin/env python3
"""
Locate stars/sources in image

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-09 JMT From scratch

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

"""
ORB feature detection and binary descriptor test
"""

from skimage import transform as tf
from skimage.feature import match_descriptors, ORB, plot_matches
from skimage.color import rgb2gray
from skimage.io import imread
from scipy.misc import imresize


def starfinder(img16):

    if img16.size > 0:

        print('Hello from starfinder!')

    else:

        print('* Empty image passed to starfinder - returning')


