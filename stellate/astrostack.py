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

from stellate.astroimage import AstroImage


class AstroStack():

    def __init__(self, fnames, in_mem=True):

        # Public attributes (get and set)
        self.ref_index = 0

        # Protected attributes
        self._fnames = fnames
        self._stack = []

        for fname in fnames:
            print('  Loading %s into memory' % fname)
            self._stack.append(AstroImage(fname, in_mem))

    def __len__(self):
        return len(self._stack)

    def get_fname(self, idx=0):
        if self.idx_in_range(idx):
            fname = self._stack[idx].get_fname()
        else:
            fname = []
        return fname

    def get_hdr(self, idx=0):
        if self.idx_in_range(idx):
            hdr = self._stack[idx].get_hdr()
        else:
            hdr = []
        return hdr

    def get_img(self, idx=0):
        if self.idx_in_range(idx):
            img = self._stack[idx].get_img()
        else:
            img = []
        return img

    def get_stars(self, idx=0):
        if self.idx_in_range(idx):
            stars = self._stack[idx].find_stars()
        else:
            stars = []
        return stars

    def idx_in_range(self, idx):
        return idx >= 0 and idx < len(self)

    def register(self):

        # Run star finder on each image in the stack
        for fname in self._fnames:

            aimg = AstroImage(fname)
            stars = aimg.find_stars(write_json=True)

    def combine(self):

        print('Combining images using median')
        pass
