#!/usr/bin/env python3
"""
Blob detection tests (LOG, DOG and DOH)
"""

from scipy.misc import imresize
from skimage.io import imread
from skimage.feature import register_translation
from skimage import transform as tf
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import time

print('Loading image')
ref = rgb2gray(imread('saturn.png'))

print('Displacing')
tform = tf.AffineTransform(scale=(1, 1), rotation=0.0, translation=(-50, -250))
img = tf.warp(ref, tform)

print('Running xcorr')

t0 = time.time()
disp, err, pd = register_translation(img, ref)
dy, dx = disp
t_xcorr = time.time() - t0

print('Estimated displacement (dx, dy) : (%0.1f, %0.1f)' % (dx, dy))

t0 = time.time()
moco = tf.EuclideanTransform(translation=[dx, dy])
img_moco = tf.warp(img, moco)
t_moco = time.time() - t0

print('xcorr : %0.3f s' % t_xcorr)
print('moco  : %0.3f s' % t_moco)

fig, axes = plt.subplots(1, 3, figsize=(9, 3), sharex=True, sharey=True)

axes[0].imshow(ref, interpolation='nearest')
axes[1].imshow(img, interpolation='nearest')
axes[2].imshow(img_moco, interpolation='nearest')

plt.tight_layout()
plt.show()