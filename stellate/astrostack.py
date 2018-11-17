#!/usr/bin/env python3
"""
Image registration and combining

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

from stellate.astroimage import astroimage

class astrostack():

    def __init__(self, fnames):

        self._fnames = fnames
        self._imgs = []
        self._ref_index = 0

        # Populate image stack
        for fname in fnames:
            self._imgs.append(astroimage(fname))

        self.img_idx = 0
        self._n_imgs = len(self._imgs)

    def register(self):

        stars = []

        for img in img_stack:

            stars_info, FWHM = starfinder(img)
            stars.append(stars_info)

    def combine(self):

        if "sigmoid" in self._combiner:
            print('Combing images using sigmoid')
            pass

        if "median" in self._combiner:
            print('Combing images using median')
            pass