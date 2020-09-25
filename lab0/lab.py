'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

# returns pixel value at x,y coordinate
# accounts for out of range values by extending existing image
def get_pixel(image, x, y):
    row = x
    col = y

    if row < 0:
        row = 0
    if col < 0:
        col = 0

    if row >= image['height']:
        row = image['height']-1
    if col >= image['width']:
        col = image['width'] - 1

    return image['pixels'][row*image['width']+col]


def set_pixel(image, x, y, c):
    print(image['pixels'][x*image['width']+y])
    image['pixels'][x*image['width']+y] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            result['pixels'].append(newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

# for each pixel, get a subarray with same dimensions as kernel, centered around current pixel
# multiply subarray with kernel to produce a scalar output
# update pixel to scalar output
# return new list of pixels
def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel represented by 2D array
    """
    updated_pixels = []

    for x in range(image['height']):
        for y in range(image['width']):
            updated_pixels.append(multiply_array(get_subarray(image, x, y, kernel),kernel))

    im = {  'height': image['height'],
            'width': image['width'],
            'pixels': updated_pixels}

    return im

# returns subarray of image with x,y coordinate at center and size that matches kernel size
# default kernel is identity matrix
def get_subarray(image, x, y, kernel=[[0,0,0],[0,1,0],[0,0,0]]):
    subarray = []
    k_col = int(len(kernel)/2)
    k_row = int(len(kernel[0])/2)

    for i in range(x - k_col, x+k_col+1):
        list = []
        for j in range(y - k_row, y + k_row + 1):
            list.append(get_pixel(image, i, j))
        subarray.append(list)

    return subarray

# multiplies two arrays by each element
# checks to see if they are the same dimension
def multiply_array(array, kernel):
    if len(array) != len(kernel) or len(array[0]) != len(kernel[0]):
        return False
    val = 0
    for x in range(len(array)):
        for y in range(len(array[0])):
            val += array[x][y] * kernel[x][y]
    return val



def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for x in range(len(image['pixels'])):
        val = image['pixels'][x]
        image['pixels'][x] = round(val)
        if val > 255:
            image['pixels'][x] = 255
        elif val < 0:
            image['pixels'][x] = 0

    return image


# FILTERS

def blurred(image, n, clip=True):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = blurred_kernel(n)

    # then compute the correlation of the input image with that kernel
    mod_image = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    if clip is True:
        return round_and_clip_image(mod_image)
    else:
        return mod_image


# creates kernel of size nxn
# each val is 1/n**2
def blurred_kernel(n):
    val = 1/n**2
    kernel = []
    for x in range(n):
        list = []
        for y in range(n):
            list.append(val)
        kernel.append(list)

    return kernel


# calculate blurred image pixels
# alters each pixel to 2*original pixel - blurred pixel
def sharpened(image, n):
    # use blurred function, without rounding
    blurred_im = blurred(image,n,clip=False)

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for x in range(len(image['pixels'])):
        result['pixels'].append(2*image['pixels'][x] - blurred_im['pixels'][x])

    return round_and_clip_image(result)

# produce two difference correlations
# for each pixel, calculate resulting value from combining the two correlations
def edges(image):
    kx = [[-1,0,1],[-2,0,2],[-1,0,1]]
    ky = [[-1,-2,-1],[0,0,0],[1,2,1]]

    corr1 = correlate(image, kx)
    corr2 = correlate(image, ky)

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []}

    for x in range(len(image['pixels'])):
        result['pixels'].append(round(math.sqrt((corr1['pixels'][x]**2)+(corr2['pixels'][x])**2)))

    return round_and_clip_image(result)


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    im = load_image('test_images/centered_pixel.png')
    print(im)
    print(edges(im))

    pass
