#!/usr/bin/env python3.5
"""
Perform blind deconvolution and within-stack registration of astrophotos

Usage
----
stellate.py -i <Raw image directory> -o <Output directory>
stellate.py -h

Authors
----
Mike Tyszka, Caltech

Dates
----
2017-05-01 JMT From scratch

License
----
This file is part of stellate.

    stellate is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    stellate is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with atlaskit.  If not, see <http://www.gnu.org/licenses/>.

Copyright
----
2017 California Institute of Technology.
"""

__version__ = '0.1.0'

import os
import sys
import argparse
from glob import glob


def main():

    print()
    print('---------------------------------------------')
    print('STELLATE blind deconvolution and registration')
    print('---------------------------------------------')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Blind deconvolution and registration of astrophoto stacks')
    parser.add_argument('-i','--indir', help='Input directory containing PNG image stack')
    parser.add_argument('-o','--outdir', help='Output directory"]')

    # Parse command line arguments
    args = parser.parse_args()

    if args.indir:
        png_dir = args.indir
        if not os.path.isdir(png_dir):
            print('RAW input directory does not exist (%s) - exiting' % png_dir)
            sys.exit(1)
    else:
        # Default to current directory
        png_dir = os.path.realpath(os.getcwd())

    if args.outdir:
        out_dir = args.outdir
    else:
        # Default to current directory + '.proc'
        out_dir = os.path.realpath(os.getcwd() + '.proc')

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print('Input directory  : %s' % png_dir)
    print('Output directory : %s' % out_dir)

    # Get image list from input directory
    png_list = glob(os.path.join(png_dir,'*.png'))

    print('Found %d PNGs in %s' % (len(png_list), png_dir))

    # Load the first image to use as a motion reference
    img_ref = load_png(png_list[0])

    for png_fname in png_list:

        print('  Processing %s' % os.path.basename(png_fname))

        # Load the RGB frame from the current PNG file
        img = load_png(png_fname)

        # Rigid-body motion correct frame
        img_moco = moco(img, img_ref)

        # Save corrected PNG
        out_bname = os.path.basename(png_fname)
        out_fname = os.path.join(out_dir, out_bname.replace('.png', '_corr.png'))
        save_png(out_fname, img_moco)

    # Clean exit
    sys.exit(0)


def moco(img, img_ref):

    from cv2 import estimateRigidTransform, warpAffine

    ny, nx, _ = img.shape

    M = estimateRigidTransform(img, img_ref, fullAffine=False)

    img_moco = warpAffine(img, M, (nx, ny))

    return img_moco


def load_png(png_fname, sf=0.25):

    from cv2 import imread, resize

    try:
        img = imread(png_fname)
    except:
        print('* Problem loading %s' % png_fname)
        img = []

    # Optional resampling
    if sf < 1.0:
        print('  Resizing (sf = %0.2f)' % sf)
        img = resize(img, (0,0), fx=sf, fy=sf)

    return img


def save_png(png_fname, img):

    from cv2 import imwrite

    try:
        imwrite(png_fname, img)
    except:
        print('* Problem saving %s' % png_fname)


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
