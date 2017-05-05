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
from skimage import io


def main():

    print()
    print('---------------------------------------------')
    print('STELLATE blind deconvolution and registration')
    print('---------------------------------------------')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Blind deconvolution and registration of astrophoto stacks')
    parser.add_argument('-i','--indir', help='Input directory containing RAW image stack')
    parser.add_argument('-o','--outdir', help='Output directory"]')

    # Parse command line arguments
    args = parser.parse_args()

    if args.indir:
        raw_dir = args.indir
        if not os.path.isdir(raw_dir):
            print('RAW input directory does not exist (%s) - exiting' % raw_dir)
            sys.exit(1)
    else:
        # Default to current directory
        raw_dir = os.path.realpath(os.getcwd())

    if args.outdir:
        out_dir = args.outdir
    else:
        # Default to current directory + '.proc'
        out_dir = os.path.realpath(os.getcwd() + '.proc')

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print('Input directory  : %s' % raw_dir)
    print('Output directory : %s' % out_dir)

    # Load all RAW images from input directory
    stack_rgb = load_png_stack(raw_dir)

    # Correct for inter-frame motion
    stack_rgb_moco = register_stack(stack_rgb)

    # Blind deconvolution
    # stack_decon = blind_deconvolve(stack_rgb_moco)

    # Save stack
    save_stack(stack_rgb_moco, out_dir)

    # Clean exit
    sys.exit(0)


def register_stack(stack_rgb):

    from skimage.feature import register_translation
    from skimage.transform import SimilarityTransform, warp
    from skimage.color import rgb2gray

    ref_gray = rgb2gray(stack_rgb[0])

    stack_rgb_moco = list()

    for img_rgb in stack_rgb:

        img_gray = rgb2gray(img_rgb)

        # 2D register
        shifts, error, phasediff = register_translation(img_gray, ref_gray)

        # Construct transform object
        tx = SimilarityTransform(translation=shifts)

        # Apply translation
        img_rgb_tx = warp(img_rgb, tx)

        # Add to transformed image list
        stack_rgb_moco.append(img_rgb_tx)

    return stack_rgb_moco


def blind_deconvolve(stack_rgb):

    stack_decon = list()

    for rgb in stack_rgb:
        pass

    return stack_decon


def load_png_stack(png_dir):
    """
    Load PNG series from directory provided

    :param png_dir:
    :return:
    """

    # Init empty list for image stack_rgb
    stack_rgb = list()

    for fname in os.listdir(png_dir):

        try:
            img = io.imread(fname)
        except:
            img = []
            pass

        if len(img) > 0:
            print('Loaded %s' % fname)
            stack_rgb.append(img)

    if len(stack_rgb) < 1:
        print('No images were loaded')

    return stack_rgb


def save_stack(stack_rgb, out_dir):

    from skimage.io import imshow, imsave

    for ic, img in enumerate(stack_rgb):

        fname = os.path.join(out_dir, 'img_%03d.png' % ic)
        imsave(fname, img)

    return


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
