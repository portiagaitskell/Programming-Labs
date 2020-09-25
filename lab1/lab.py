'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3

import math

from PIL import Image

# VARIOUS FILTERS

'''LAB0 Code
'''

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
    #print(image['pixels'][x*image['width']+y])
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
#for each pixel, calculate resulting value from combining the two correlations
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


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(image):
        r, g, b = split_color(image)
        r = filt(r)
        g = filt(g)
        b = filt(b)

        color = combine_color((r,g,b))

        return color

    return color_filter

# returns 3 seperate lists of r, g, b
def split_color(image):
    r = {'height': image['height'], 'width': image['width'], 'pixels': []}
    g = {'height': image['height'], 'width': image['width'], 'pixels': []}
    b = {'height': image['height'], 'width': image['width'], 'pixels': []}

    for p in image['pixels']:
        r['pixels'].append(p[0])
        g['pixels'].append(p[1])
        b['pixels'].append(p[2])

    return r, g, b

# takes tuple representing 3 images (r,g,b) and return a single image, combining all of them
def combine_color(images):
    r = images[0]['pixels']
    g = images[1]['pixels']
    b = images[2]['pixels']

    color = {'height': images[0]['height'], 'width': images[0]['width'], 'pixels': []}

    for x in range(len(r)):
        color['pixels'].append((r[x], g[x], b[x]))

    return color

# create new function to blur images using one parameter
# allows you to pass filter into color_filter_from_greyscale - can now blur colored images
def make_blur_filter(n):

    def blur(image):
        return blurred(image, n)

    return blur


def make_sharpen_filter(n):

    def sharpen(image):
        return sharpened(image, n)

    return sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(image):
        image = image
        for filter in filters:
            image = filter(image)

        return image

    return cascade


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    # create copy of original image
    im = {'height': image['height'],'width': image['width'],'pixels': []}
    for x in image['pixels']:
        im['pixels'].append(x)

    for i in range(ncols):
        grey = greyscale_image_from_color_image(im)

        em = compute_energy(grey)

        cem = cumulative_energy_map(em)

        pixels = minimum_energy_seam(cem)

        im = image_without_seam(im, pixels)

    return im


# Optional Helper Functions for Seam Carving

# convert color image to greyscale using formula
def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    def greyscale(colors):
        color = round(.299*colors[0]+.587*colors[1]+.114*colors[2])
        return color
    return apply_per_pixel(image, greyscale)


# use edges function to compute energy
def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)

#
def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map" as described in the lab 1 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    # turn pixels list into 2-D array, so each row can be access
    new = list_to_2D(energy)
    pixels = energy['pixels']
    height = energy['height']
    width = energy['width']

    #first row stays the same
    cumulative = [new[0]]

    # run through each row, starting from row 1
    # at the end, append each new row to cumulative
    # checks adjacent pixels for min path
    for i in range(1,height):
        row = []
        for j in range(width):
            min = cumulative[i-1][j]
            if j != 0:
                if cumulative[i-1][j-1] <= min:
                    min = cumulative[i-1][j-1]
            if j!= width-1:
                if cumulative[i-1][j+1] < min:
                    min = cumulative[i-1][j+1]
            row.append(min+new[i][j])
        cumulative.append(row)

    # flatten 2d array
    final = [j for sub in cumulative for j in sub]

    return {'height': height, 'width': width, 'pixels': final}


def minimum_energy_seam(c):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 1 writeup).
    """
    pixels = c['pixels']
    height = c['height']
    width = c['width']

    new = list_to_2D(c)

    rm_pixel = []

    # find lowest energy value in bottom row, row = height - 1
    btm_row = new[height-1]
    min_val = btm_row[0]
    min_index = 0

    for x in range(len(btm_row)):
        if btm_row[x] < min_val:
            min_val = btm_row[x]
            min_index = x

    rm_pixel.append((height-1)*width+min_index)

    # start at row number height-2, move backwards to the first row
    # find the minimum pixel that is adjacent to the previous one
    for i in range(height - 2, -1, -1):
        row = new[i]
        min_val = row[min_index]
        temp = min_index
        if min_index != 0:
            if row[min_index-1] <= min_val:
                min_val = row[min_index-1]
                temp = min_index-1
        if min_index != width-1:
            if row[min_index+1] < min_val:
                min_val = row[min_index+1]
                temp = min_index+1

        min_index = temp

        rm_pixel.append(i*width+min_index)

    return rm_pixel

# HELPER FUNCTION - convert list to 2D array
def list_to_2D(image):
    pixels = image['pixels']
    height = image['height']
    width = image['width']

    new = []
    for i in range(height):
        row = []
        for j in range(width):
            row.append(pixels[i * width + j])
        new.append(row)

    return new

def image_without_seam(im, s):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    pixels = im['pixels']
    for x in s:
        del pixels[x]

    return {'height': im['height'], 'width': im['width']-1, 'pixels': pixels}


def emboss(image, n, direction = 'horizontal'):
    grey = greyscale_image_from_color_image(image)

    #emboss_kernel = [[0,1,0],[0,0,0],[0,-1,0]]
    #emboss_kernel = [[1, 0, 0],[0, 0, 0],[0, 0, -1]]
    #emboss_kernel = h = [[0, 0, 1],[0, 0, 0],[-1, 0, 0]]
    #emboss_kernel = [[1, 0, 0, 0, 0],[0, 1, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, -1, 0],[0, 0, 0, 0, -1]]
    #emboss_kernel = [[0, 0, +1, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, 0, 0, 0],[0, 0, -1, 0, 0]]

    #create nxn array of 0s
    kernel = [[0 for i in range(n)] for j in range(n)]
    if direction == 'vertical':
        kernel[0][int(n/2)] = 1
        kernel[n-1][int(n/2)] = -1
    else:
        kernel[int(n/2)][0] = 1
        kernel[int(n/2)][n-1] = -1

    result = correlate(grey, kernel)

    for i in range(len(result['pixels'])):
        result['pixels'][i] += 128

    return result


def blue_highlight(image):
    pix = image['pixels']
    for x in range(len(pix)):
        print(pix[x][2])
        b = round(2*(pix[x][2]))
        print(b)
        pix[x] = (pix[x][0], pix[x][1], b)

    print(pix)
    return {'height': image['height'],'width': image['width'], 'pixels': pix}

def threshold(image, t=200):

    def threshold1(color):
        if color >= t:
            return 255
        else:
            return 0

    return apply_per_pixel(image, threshold1)


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()
    print('DONE')


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # then the following will create a color version of that filter

    '''
    # test blurring colored images
    color_blur = color_filter_from_greyscale_filter(make_blur_filter(9))

    im = load_color_image('test_images/python.png')
    blurry = color_blur(im)
    save_color_image(blurry, 'test_images/blurry_python.png')
    '''
    '''
    # test sharpening colored images
    color_sharpen = color_filter_from_greyscale_filter(make_sharpen_filter(7))

    im = load_color_image('test_images/sparrowchick.png')
    save_color_image(color_sharpen(im), 'test_images/sharpen_sparrowchick.png')
    '''
    '''
    im = load_color_image('test_images/twocats.png')

    image = seam_carving(im, 100)


    save_color_image(image,'test_images/two_cats_seam.png')

    im = load_color_image('test_images/pattern.png')

    grey = greyscale_image_from_color_image(im)

    em = compute_energy(grey)

    cem = cumulative_energy_map(em)

    pixels = minimum_energy_seam(cem)
    print(pixels)
    i = image_without_seam(im, pixels)

    save_color_image(i,'test_images/pattern_2.png')
    '''
    '''
    im = load_color_image('test_images/lighthouse.png')
    save_image(emboss(im),'test_images/lighthouse3.png')
    '''

    '''

    threshold_color = color_filter_from_greyscale_filter(threshold)

    im = load_color_image('test_images/frog.png')
    #save_image(threshold(im),'test_images/frog2.png')
    save_color_image(threshold_color(im),'test_images/frog2.png')
    '''

    im = load_color_image('test_images/dock.png')
    save_image(emboss(im,5,'vertical'),'test_images/dock_vertical.png')

    pass
