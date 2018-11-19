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

import numpy as np
from stellate.astroimage import AstroImage
from skimage.measure import ransac
from skimage.transform import AffineTransform, PolynomialTransform


class AstroStack():

    def __init__(self, fnames, in_mem=True):

        # Public attributes (get and set)
        self.ref_index = 0

        # Protected attributes
        self._fnames = fnames
        self._stack = []

        # Load images into a list of AstroImages
        for fname in fnames:
            print('  Loading %s into memory' % fname)
            self._stack.append(AstroImage(fname, in_mem))

    def __len__(self):
        return len(self._stack)

    def register(self):

        print('')
        print('Image stack registration')

        if len(self) <= 1:
            print('  More than one image required for stack registration - returning')
            return

        # Make sure all images in stack have star fields by
        # running find_stars on each
        stars = [aimg.find_stars(write_sidecar=True) for aimg in self._stack]

        stars_ref = stars[self.ref_index]

        for stars_src in stars:

            # Calculate transform mapping this starfield to the reference starfield
            T = self.calc_transform(stars_src, stars_ref)

            # Report translation and rotation components of affine transform
            print(T.translation)
            print(T.rotation)

    def calc_transform(self, stars_src, stars_ref):
        """
        Calculate the transform mapping a star field to a reference star field using RANSAC

        :param stars_src: Pandas dataframe, source starfield
        :param stars_ref: Pandas dataframe, reference starfield
        :return: transform
        """

        # Extract source and reference star centroids
        # src and ref are lists of [x,y] coordinates
        # of star centroids
        src = np.array([[row['cc'], row['rc']] for _, row in stars_src.iterrows()])
        ref = np.array([[row['cc'], row['rc']] for _, row in stars_ref.iterrows()])

        # Randomly subsample the larger star list to match the smaller star list
        ns, nr = len(src), len(ref)
        if ns > nr:
            inds = np.random.choice(ns, nr, replace=False)
            src = src[inds, :]
        elif nr > ns:
            inds = np.random.choice(nr, ns, replace=False)
            ref = ref[inds, :]

        # Estimate  transform model with RANSAC
        T, inliers = ransac((src, ref),
                            AffineTransform,
                            min_samples=9,
                            residual_threshold=2,
                            max_trials=100)

        outliers = inliers == False

        print(inliers.sum())

        return T

    def combine(self):

        print('Combining images using median')
        pass

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


class BicubicTransform(PolynomialTransform):

    def __init__(self):
        super().__init__()

    def estimate(self, src, dst, order=3):
        super().estimate(src, dst, order)

    def residuals(self, src, dst):
        super().residuals(src, dst)