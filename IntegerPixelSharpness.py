#!/usr/bin/python
'''Integer Pixel Sharpness V0.6 https://github.com/B0M
    Copyright (C) 2017  B0M

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

#from __future__ import division
from PIL import Image
import math
import multiprocessing
import sys
import os.path
source_file = ""
output_file = ""
sequence_length = 8
x_size = 424
y_size = 240
scale = 4
x_scaled = 1920
y_scaled = 1080
alpha = False
digits = None

cmd_args = []

def reinterpret_image(imgIn, xSizeIn, ySizeIn):
    picTemp = [None] * xSizeIn
    for n in range(xSizeIn):
        picTemp[n] = [None] * ySizeIn
    picIn = imgIn.load()
    for i in range(xSizeIn):
        for j in range(ySizeIn):
            picTemp[i][j] = picIn[((imgIn.size[0]*i)/xSizeIn)+((imgIn.size[0]/xSizeIn)/2),((imgIn.size[1]*j)/ySizeIn)+((imgIn.size[1]/ySizeIn)/2)]
    return picTemp

def rescale(arrIn, xSizeIn, ySizeIn):
    picTemp2 = [None] * xSizeIn
    for n in range(xSizeIn):
        picTemp2[n] = [None] * ySizeIn
    for i in range(xSizeIn):
        for j in range(ySizeIn):
            picTemp2[i][j] = arrIn[int((len(arrIn)*i)/xSizeIn)][int((len(arrIn[0])*j)/ySizeIn)]
    return picTemp2

def write_image(arrIn2, fileout):
    if alpha:
        imgOut = Image.new('RGBA', (len(arrIn2), len(arrIn2[0])), (0,0,0,0))
    else:
        imgOut = Image.new('RGB', (len(arrIn2), len(arrIn2[0])), (0,0,0))
    picOut = imgOut.load()
    for i in range(len(arrIn2)):
        for j in range(len(arrIn2[0])):
            picOut[i,j] = arrIn2[i][j]
    if os.path.isfile(fileout):
        imgOut.close()
        raise IOError('File already exists!')
    else:
        imgOut.save(fileout)
        imgOut.close()
        print "Saved to as: " + fileout
    

def check_digits(path_in, num):
    pure_name = os.path.split(path_in)[1].rsplit(".", 1)[0]
    length = len(str(num))
    for i in range(1, length+1):
        try:
            int(pure_name[-i])
        except ValueError:
            raise OSError('File is not valid start of a sequence! Should -m be there? Is your sequence length too long?')
    if not os.path.isfile(os.path.split(path_in)[0] + os.sep + os.path.split(path_in)[1].rsplit(".", 1)[0][:-length] + str(num-1) + "." + os.path.split(path_in)[1].rsplit(".", 1)[1]):
        raise IOError('Last file of sequence does not exist! Is your sequence length too long?')
    return length

def intc(a):
    out = None
    try:
        out = int(a)
    except ValueError:
        out = "Fail"
    return out


def renderer(num):
    s_endname = os.path.split(source_file)[1].rsplit(".", 1)[0][:-digits] + str(num).zfill(digits) + "." + os.path.split(source_file)[1].rsplit(".", 1)[1]
    s_outpath = os.path.split(source_file)[0] + os.sep + s_endname
    endname = os.path.split(output_file)[1].rsplit(".", 1)[0] + str(num).zfill(digits) + "." + os.path.split(output_file)[1].rsplit(".", 1)[1]
    outpath = os.path.split(output_file)[0] + os.sep + endname
    print s_outpath
    img = Image.open(s_outpath, 'r')
    if ("-d" in cmd_args) or ("-D" in cmd_args):
        write_image(rescale(reinterpret_image(img, x_size, y_size), x_scaled, y_scaled), outpath)
    else:
        write_image(reinterpret_image(img, x_size, y_size), outpath)
    img.close()
    return


if __name__ == '__main__':
    if not 'idlelib.run' in sys.modules:
        cmd_args = sys.argv
        if len(sys.argv) == 1:
            print '''Usage:
	python ...'''+ os.sep + '''IntegerPixelSharpness.py [source_filename] [-a] [-c <resolution>] [-d <scale>] [-D <resolution>] [-m <length>] [output_filename]
Help:
	Pixelises an image (or sequence) and can even upscale the result.
	Similar to the Mosaic function in Premiere Pro but more accurate.
Options:
	-a		Output image with alpha channel.
	-c		The first resolution to convert the image into.
			This is the important part where the image
			gets transformed into a lower resolution to
			remove the blurriness from a high-ish reolution
			image (or sequence) that's displaying low
			resolution content.
			Format is int + "x" + int. ie. 1280x720
			If omitted defaults to 424x240.
	-d		The second step where the image is upscaled
			using nearest neighbour to a certain scaling
			factor. -D cannot be used simutaneously with
			this or an error will return. If both are
			omitted then image will not be upscaled.
	-D		The second step where the image is upscaled
			using nearest neighbour to another resolution.
			-d cannot be used simutaneously with this or an
			error will return. If both are omitted then
			image will not be upscaled.
			Format is int + "x" + int. ie. 1280x720
	-m		Indicates that an image sequence should be
			rendered. The source_filename would be the
			first in the sequence and should have a file
			name like image00000.png. The amount of images
			in the sequence must also be specified.'''
        else:
            #Make sure args are suitable
            if ("-d" in cmd_args) and ("-D" in cmd_args):
                raise SyntaxError('-d and -D cannot be used together!')
            
            if not os.path.isfile(cmd_args[1]):
                raise IOError('Source file does not exist!')
            if (not os.path.isdir(os.path.dirname(cmd_args[-1]))):
                raise IOError('Output directory does not exist!')
            
            
            source_file = cmd_args[1]
            print "Source: " + source_file
            output_file = cmd_args[-1]
            print "Destination: " + output_file
            
            if "-a" in cmd_args:
                alpha = True
            print "Alpha: " + str(alpha)
            if "-c" in cmd_args:
                if (not isinstance(intc(cmd_args[cmd_args.index("-c")+1].split("x", 1)[0]), int)) or (not isinstance(intc(cmd_args[cmd_args.index("-c")+1].split("x", 1)[1]), int)):
                    raise ArithmeticError('-c has invalid dimentions')
                else:
                    x_size = int(cmd_args[cmd_args.index("-c")+1].split("x", 1)[0])
                    y_size = int(cmd_args[cmd_args.index("-c")+1].split("x", 1)[1])
            print "Rendering resolution: " + str(x_size) + "x" + str(y_size) + "."
            if "-D" in cmd_args:
                if (not isinstance(intc(cmd_args[cmd_args.index("-D")+1].split("x", 1)[0]), int)) or (not isinstance(intc(cmd_args[cmd_args.index("-D")+1].split("x", 1)[1]), int)):
                    raise ArithmeticError('-D has invalid dimentions')
                else:
                    x_scaled = int(cmd_args[cmd_args.index("-D")+1].split("x", 1)[0])
                    y_scaled = int(cmd_args[cmd_args.index("-D")+1].split("x", 1)[1])
                    print "Upscaled resolution: " + str(x_scaled) + "x" + str(y_scaled) + "."
            if "-d" in cmd_args:
                if (not isinstance(intc(cmd_args[cmd_args.index("-d")+1]), int)):
                    raise ArithmeticError('-d is not an integer')
                else:
                    scale = int(cmd_args[cmd_args.index("-d")+1])
                    x_scaled = x_size*scale
                    y_scaled = y_size*scale
                    print "Upscaled resolution: " + str(x_scaled) + "x" + str(y_scaled) + "."
            if "-m" in cmd_args:
                if (not isinstance(intc(cmd_args[cmd_args.index("-m")+1]), int)):
                    raise ArithmeticError('-m is not an integer')
                else:
                    sequence_length = int(cmd_args[cmd_args.index("-m")+1])
                    print "Sequence Length: " + str(sequence_length)
                    digits = check_digits(cmd_args[1], sequence_length)
                
                jobs = []
                processors = multiprocessing.cpu_count()
                for h in range(0, sequence_length, processors):
                    n = h + processors
                    if n > sequence_length:
                        n = sequence_length
                    for i in range(h, n):
                        process = multiprocessing.Process(target=renderer, args=(i,))
                        jobs.append(process)
                        process.start()
                    for j in range(h, h + processors):
                        jobs[j].join()
                    print "Rendered " + str(h) + " to " + str(n-1) + "."
            else:
                img = Image.open(source_file, 'r')
                if ("-d" in cmd_args) or ("-D" in cmd_args):
                    write_image(rescale(reinterpret_image(img, x_size, y_size), x_scaled, y_scaled), output_file)
                else:
                    write_image(reinterpret_image(img, x_size, y_size), output_file)
                img.close()
    else:
        print "Run this in the command line!"
