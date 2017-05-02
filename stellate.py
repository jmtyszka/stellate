#!/usr/bin/env python3
"""
Perform blind deconvolution and within-stack registration of astrophotos

Usage
----
stellate.py -i <RAW image directory> -o <Output directory>
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
import numpy as np


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

    print('Input directory : %s' % raw_dir)

    if args.outdir:
        out_dir = args.outdir
    else:
        # Default to current directory
        out_dir = os.path.realpath(os.getcwd())

    print('Output directory    : %s' % out_dir)

    # Load all RAW images from input directory
    load_raw_stack(raw_dir)

    #


    # Clean exit
    sys.exit(0)


def blind_deconvolve(stack):

    return []


def register_stack(stack):

    return []


def load_raw_stack(raw_dir):

    return []


def write_output(out_dir):

    return []


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
