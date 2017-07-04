#!/usr/bin/env python

#!/usr/bin/python

# Processes an image to extract the text portions. Primarily
# used for pre-processing for performing OCR.

# Based on the paper "Font and Background Color Independent Text Binarization" by
# T Kasar, J Kumar and A G Ramakrishnan
# http://www.m.cs.osakafu-u.ac.jp/cbdar2007/proceedings/papers/O1-1.pdf

# Copyright (c) 2012, Jason Funk <jasonlfunk@gmail.com>
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cv2
import numpy as np
import sys
import os.path

'''if len(sys.argv) != 3:
    print "%s input_file output_file" % (sys.argv[0])
    sys.exit()
else:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

if not os.path.isfile(input_file):
    print "No such file '%s'" % input_file
    sys.exit()'''

DEBUG = 0
contours = []
img_x = 0
img_y = 0

# Determine pixel intensity
# Apparently human eyes register colors differently.
# TVs use this formula to determine
# pixel intensity = 0.30R + 0.59G + 0.11B
def ii(xx, yy):
    global img, img_y, img_x
    if yy >= img_y or xx >= img_x:
        #print "pixel out of bounds ("+str(y)+","+str(x)+")"
        return 0
    pixel = img[yy][xx]
    return 0.30 * pixel[2] + 0.59 * pixel[1] + 0.11 * pixel[0]


# A quick test to check whether the contour is
# a connected shape
def connected(contour):
    first = contour[0][0]
    last = contour[len(contour) - 1][0]
    return abs(first[0] - last[0]) <= 1 and abs(first[1] - last[1]) <= 1


# Helper function to return a given contour
def c(index):
    global contours
    return contours[index]


# Count the number of real children
def count_children(index, h_, contour):
    # No children
    if h_[index][2] < 0:
        return 0
    else:
        #If the first child is a contour we care about
        # then count it, otherwise don't
        if keep(c(h_[index][2])):
            count = 1
        else:
            count = 0

            # Also count all of the child's siblings and their children
        count += count_siblings(h_[index][2], h_, contour, True)
        return count


# Quick check to test if the contour is a child
def is_child(index, h_):
    return get_parent(index, h_) > 0


# Get the first parent of the contour that we care about
def get_parent(index, h_):
    parent = h_[index][3]
    while not keep(c(parent)) and parent > 0:
        parent = h_[parent][3]

    return parent


# Count the number of relevant siblings of a contour
def count_siblings(index, h_, contour, inc_children=False):
    # Include the children if necessary
    if inc_children:
        count = count_children(index, h_, contour)
    else:
        count = 0

    # Look ahead
    p_ = h_[index][0]
    while p_ > 0:
        if keep(c(p_)):
            count += 1
        if inc_children:
            count += count_children(p_, h_, contour)
        p_ = h_[p_][0]

    # Look behind
    n = h_[index][1]
    while n > 0:
        if keep(c(n)):
            count += 1
        if inc_children:
            count += count_children(n, h_, contour)
        n = h_[n][1]
    return count


# Whether we care about this contour
def keep(contour):
    return keep_box(contour) and connected(contour)


# Whether we should keep the containing box of this
# contour based on it's shape
def keep_box(contour):
    xx, yy, w_, h_ = cv2.boundingRect(contour)
    # width and height need to be floats
    w_ *= 1.0
    h_ *= 1.0

    # Test it's shape - if it's too oblong or tall it's
    # probably not a real character
    if w_ / h_ < 0.1 or w_ / h_ > 10:
        if DEBUG:
            print("\t Rejected because of shape: (" + str(xx) + "," + str(yy) + "," + str(w_) + "," + str(h_) + ")" + \
                  str(w_ / h_))
        return False
    
    # check size of the box
    if ((w_ * h_) > ((img_x * img_y) / 5)) or ((w_ * h_) < 15) or w_ > 250 or w_ < 3 or h_ > 335 or h_ < 3:
        if DEBUG:
            print("\t Rejected because of size")
        return False

    return True


def include_box(index, h_, contour):
    if DEBUG:
        print(str(index) + ":")
        if is_child(index, h_):
            print("\tIs a child")
            print("\tparent " + str(get_parent(index, h_)) + " has " + str(
                count_children(get_parent(index, h_), h_, contour)) + " children")
            print("\thas " + str(count_children(index, h_, contour)) + " children")

    if is_child(index, h_) and count_children(get_parent(index, h_), h_, contour) <= 4:
        if DEBUG:
            print("\t skipping: is an interior to a letter")
        return False

    if count_children(index, h_, contour) > 4:
        if DEBUG:
            print("\t skipping, is a container of letters")
        return False

    if DEBUG:
        print("\t keeping")
    return True
    
def prune_image(input_file, output_file):
   global contours, img_y, img_x, img
   # Load the image
   orig_img = cv2.imread(input_file)
   
   # Add a border to the image for processing sake
   img = cv2.copyMakeBorder(orig_img, 50, 50, 50, 50, cv2.BORDER_CONSTANT)

   # Calculate the width and height of the image
   img_y = len(img)
   img_x = len(img[0])

   if DEBUG:
       print("Image is " + str(len(img)) + "x" + str(len(img[0])))

   #Split out each channel
   blue, green, red = cv2.split(img)

   # Run canny edge detection on each channel
   blue_edges = cv2.Canny(blue, 200, 250)
   green_edges = cv2.Canny(green, 200, 250)
   red_edges = cv2.Canny(red, 200, 250)

   # Join edges back into image
   edges = blue_edges | green_edges | red_edges

   # Find the contours
   image,contours,hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

   if hierarchy is not None:
       hierarchy = hierarchy[0]
   else:
       print("ERROR READING IMAGE")
       return False

   if DEBUG:
       processed = edges.copy()
       rejected = edges.copy()

   # These are the boxes that we are determining
   keepers = []

   # For each contour, find the bounding rectangle and decide
   # if it's one we care about
   for index_, contour_ in enumerate(contours):
       if DEBUG:
           print("Processing #%d" % index_)

       x, y, w, h = cv2.boundingRect(contour_)

       # Check the contour and it's bounding box
       if keep(contour_) and include_box(index_, hierarchy, contour_):
           # It's a winner!
           keepers.append([contour_, [x, y, w, h]])
           if DEBUG:
               cv2.rectangle(processed, (x, y), (x + w, y + h), (100, 100, 100), 1)
               cv2.putText(processed, str(index_), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
       else:
           if DEBUG:
               cv2.rectangle(rejected, (x, y), (x + w, y + h), (100, 100, 100), 1)
               cv2.putText(rejected, str(index_), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

   # Make a white copy of our image
   new_image = edges.copy()
   new_image.fill(255)
   boxes = []

   # For each box, find the foreground and background intensities
   for index_, (contour_, box) in enumerate(keepers):

       # Find the average intensity of the edge pixels to
       # determine the foreground intensity
       fg_int = 0.0
       for p in contour_:
           fg_int += ii(p[0][0], p[0][1])

       fg_int /= len(contour_)
       if DEBUG:
           print("FG Intensity for #%d = %d" % (index_, fg_int))

       # Find the intensity of three pixels going around the
       # outside of each corner of the bounding box to determine
       # the background intensity
       x_, y_, width, height = box
       bg_int = \
           [
               # bottom left corner 3 pixels
               ii(x_ - 1, y_ - 1),
               ii(x_ - 1, y_),
               ii(x_, y_ - 1),

               # bottom right corner 3 pixels
               ii(x_ + width + 1, y_ - 1),
               ii(x_ + width, y_ - 1),
               ii(x_ + width + 1, y_),

               # top left corner 3 pixels
               ii(x_ - 1, y_ + height + 1),
               ii(x_ - 1, y_ + height),
               ii(x_, y_ + height + 1),

               # top right corner 3 pixels
               ii(x_ + width + 1, y_ + height + 1),
               ii(x_ + width, y_ + height + 1),
               ii(x_ + width + 1, y_ + height)
           ]

       # Find the median of the background
       # pixels determined above
       bg_int = np.median(bg_int)

       if DEBUG:
           print("BG Intensity for #%d = %s" % (index_, repr(bg_int)))

       # Determine if the box should be inverted
       if fg_int >= bg_int:
           fg = 255
           bg = 0
       else:
           fg = 0
           bg = 255

           # Loop through every pixel in the box and color the
           # pixel accordingly
       for x in range(x_, x_ + width):
           for y in range(y_, y_ + height):
               if y >= img_y or x >= img_x:
                   if DEBUG:
                       print("pixel out of bounds (%d,%d)" % (y, x))
                   continue
               if ii(x, y) > fg_int:
                   new_image[y][x] = bg
               else:
                   new_image[y][x] = fg

   # blur a bit to improve ocr accuracy
   new_image = cv2.blur(new_image, (2, 2))
   cv2.imwrite(output_file, new_image)
   if DEBUG:
       cv2.imwrite('edges.png', edges)
       cv2.imwrite('processed.png', processed)
       cv2.imwrite('rejected.png', rejected)
       
   return True



'''
Python-tesseract is an optical character recognition (OCR) tool for python.
That is, it will recognize and "read" the text embedded in images.

Python-tesseract is a wrapper for google's Tesseract-OCR
( http://code.google.com/p/tesseract-ocr/ ).  It is also useful as a
stand-alone invocation script to tesseract, as it can read all image types
supported by the Python Imaging Library, including jpeg, png, gif, bmp, tiff,
and others, whereas tesseract-ocr by default only supports tiff and bmp.
Additionally, if used as a script, Python-tesseract will print the recognized
text in stead of writing it to a file. Support for confidence estimates and
bounding box data is planned for future releases.


USAGE:
```
 > try:
 >     import Image
 > except ImportError:
 >     from PIL import Image
 > import pytesseract
 > print(pytesseract.image_to_string(Image.open('test.png')))
 > print(pytesseract.image_to_string(Image.open('test-european.jpg'), lang='fra'))
```

INSTALLATION:

Prerequisites:
* Python-tesseract requires python 2.5 or later or python 3.
* You will need the Python Imaging Library (PIL).  Under Debian/Ubuntu, this is
  the package "python-imaging" or "python3-imaging" for python3.
* Install google tesseract-ocr from http://code.google.com/p/tesseract-ocr/ .
  You must be able to invoke the tesseract command as "tesseract". If this
  isn't the case, for example because tesseract isn't in your PATH, you will
  have to change the "tesseract_cmd" variable at the top of 'tesseract.py'.
  Under Debian/Ubuntu you can use the package "tesseract-ocr".
  
Installing via pip:   
See the [pytesseract package page](https://pypi.python.org/pypi/pytesseract)     
$> sudo pip install pytesseract   

Installing from source:   
$> git clone git@github.com:madmaze/pytesseract.git   
$> sudo python setup.py install    


LICENSE:
Python-tesseract is released under the GPL v3.

CONTRIBUTERS:
- Originally written by [Samuel Hoffstaetter](https://github.com/hoffstaetter) 
- [Juarez Bochi](https://github.com/jbochi)
- [Matthias Lee](https://github.com/madmaze)
- [Lars Kistner](https://github.com/Sr4l)

'''

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

try:
    import Image
except ImportError:
    from PIL import Image
    import PIL.ImageOps
import subprocess
import sys
import tempfile
import os
import shlex

__all__ = ['image_to_string', 'cleanup_colors', 'common_color']

def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False, config=None):
    '''
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`
    
    returns the exit status of tesseract, as well as tesseract's stderr output

    '''
    command = [tesseract_cmd, input_filename, output_filename_base]
    
    if lang is not None:
        command += ['-l', lang]

    if boxes:
        command += ['batch.nochop', 'makebox']
        
    if config:
        command += shlex.split(config)
    
    proc = subprocess.Popen(command,
            stderr=subprocess.PIPE)
    return (proc.wait(), proc.stderr.read())

def cleanup(filename):
    ''' tries to remove the given filename. Ignores non-existent files '''
    try:
        os.remove(filename)
    except OSError:
        pass

def get_errors(error_string):
    '''
    returns all lines in the error_string that start with the string "error"

    '''

    lines = error_string.splitlines()
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if len(error_lines) > 0:
        return '\n'.join(error_lines)
    else:
        return error_string.strip()

def tempnam():
    ''' returns a temporary file-name '''
    tmpfile = tempfile.NamedTemporaryFile(prefix="tess_")
    return tmpfile.name

class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)

def common_color(image):
    moder = {}
    for i in range(int(image.width/4),int(image.width*3/4)):
        for j in range(int(image.height/20),int(image.height/2)):
            pixel = image.getpixel((i,j))
            total = pixel[0] + pixel[1] + pixel[2]
            if total == 0:
                norm = [33.3,33.3,33.3]
            else:
                norm = [pixel[0]/total,pixel[1]/total,pixel[2]/total]
            hexval = ('%s%s%s'%(int(norm[0]*100),int(norm[1]*100),int(norm[2]*100)))
            if hexval in moder.keys():
                moder[hexval] += 1
            else:
                moder[hexval] = 1

    mode = 0
    modeval = 'FFFFFF'

    return [c for c in moder.keys() if moder[c] > image.width*10]


def image_to_string(image, lang=None, boxes=False, config='--oem 0 digits'):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.
    
    also supports boxes and config.
    
    if boxes=True
        "batch.nochop makebox" gets added to the tesseract call
    if config is set, the config gets appended to the command.
        ex: config="-psm 6"

    '''

    if len(image.split()) == 4:
        # In case we have 4 channels, lets discard the Alpha.
        # Kind of a hack, should fix in the future some time.
        r, g, b, a = image.split()
        image = Image.merge("RGB", (r, g, b))
        
    #cleanup_colors(image)
    if image.width < 750:
        image = image.resize((int(image.width*1.8),int(image.height*1.6)),PIL.Image.ANTIALIAS) #1.5 seems to work best
    #image = image.resize((1350,710),PIL.Image.ANTIALIAS)
    image.save('new_namee.png')
    if not prune_image('new_namee.png','testy.png'):
        return ""
    image = Image.open('testy.png')
    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    if not boxes:
        output_file_name = '%s.txt' % output_file_name_base
        output_file_name2 = '%s2.txt' % output_file_name_base
    else:
        output_file_name = '%s.box' % output_file_name_base
    try:
            
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             config=config)
                                             
        status, error_string = run_tesseract(input_file_name,
                                             '%s2'%output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             config='')
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        f = open(output_file_name, encoding='utf8')
        g = open(output_file_name2, encoding='utf8')
        try:
            neuro = g.read().strip()
            return '%s\n%s\n%s' % (f.read().strip(), neuro, neuro)
        finally:
            f.close()
            g.close()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)
        cleanup(output_file_name2)
        cleanup('testy.png')
        cleanup('new_namee.png')

def cleanup_colors(image):
    thresh = 13
    midy = (0.3, 0.5)
    midx = (0.38, 0.61)
    calcmidx = (int(midx[0] * image.width), int(midx[1] * image.width))
    calcmidy = (int(midy[0] * image.height), int(midy[1] * image.height))
    for i in range(0,image.width):
        for j in range(0,image.height):
            pixel = image.getpixel((i,j))
            '''if pixel[0] == 255:
                image.putpixel((i,j),(255,255,255))'''
            if pixel[0] > 139 and pixel[2] > 160 and pixel[0] < 200:
                image.putpixel((i,j),(255,255,255))
            elif pixel[2] > 218 and ((i < calcmidx[0] or i > calcmidx[1])) or pixel[2] > 219:
                image.putpixel((i,j),(255,255,255))
            elif pixel[0] - pixel[1] > thresh or pixel[1] - pixel[2] > thresh or pixel[2] - pixel[0] > thresh:
                image.putpixel((i,j),(0,0,0))
            elif pixel[0] == 255 and (pixel[1] < 230 or pixel[2] < 200):
                image.putpixel((i,j),(0,0,0))
            '''else:
                image.putpixel((i,j),(255,255,255))'''

def main():

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            image = Image.open(filename)
            '''cleanup_colors(image)
            image = image.resize((int(image.width*1.5),int(image.height*1.5)),PIL.Image.ANTIALIAS) #1.5 seems to work best
            image.save('new_namee.png')
            prune_image('new_namee.png','testy.png')
            image = Image.open('testy.png')'''
            if len(image.split()) == 4:
                # In case we have 4 channels, lets discard the Alpha.
                # Kind of a hack, should fix in the future some time.
                r, g, b, a = image.split()
                image = Image.merge("RGB", (r, g, b))
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        output = image_to_string(image).encode('ascii', 'ignore')
        print(output)
    elif len(sys.argv) == 4 and sys.argv[1] == '-l':
        lang = sys.argv[2]
        filename = sys.argv[3]
        try:
            image = Image.open(filename)
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        print(image_to_string(image, lang=lang))
    else:
        sys.stderr.write('Usage: python tesseract.py [-l language] input_file\n')
        exit(2)

if __name__ == '__main__':
    main()
