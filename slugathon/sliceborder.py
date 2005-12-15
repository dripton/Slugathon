#!/usr/bin/env python

"""Copy only the specified hexsides from a battlehex border image into
a new image, leaving the rest transparent."""

import sys

import Image


def slice_border_image(input_path, output_path, hexsides):
    """Copy only the specified hexsides from a battlehex border image into
    a new image, leaving the rest transparent.
    
    input_path is the path to the input border image.
    output_path is the path to the output border image.
    hexsides is a non-empty set of border hexsides to copy, each in the 
    range 0 (north) through 5 (northwest), counting clockwise.
    """
    input_im = Image.open(input_path)
    if input_im.mode != "RGBA":
        input_im = input_im.convert("RGBA")
        assert input_im.mode == "RGBA"
    x_size, y_size = input_im.size
    color = (0, 0, 0, 0)
    output_im = Image.new("RGBA", input_im.size, color)

    last = 0
    for side in xrange(6):
        if side in hexsides:
            if side != 0:
                rotation = 60 * (side - last)
                input_im = input_im.rotate(rotation)
                output_im = output_im.rotate(rotation)
                last = side
            # If the adjacent hexside does not share the same border type,
            # we want to chop at the vertex to avoid overlap.  If it does,
            # we continue to the edge to get a clean corner.

            # TODO Maybe we also want to go to the edge if an adjacent
            # hex has an adjacent border of the same type.  But that would
            # require passing more information.

            # A side has the same length as the circumradius, so the 
            # vertexes are 1/4 and 3/4 of the way across.  We fudge this a
            # bit, because our border lines have nonzero thickness.
            fudge = 0.03
            if (side - 1) % 6 in hexsides:
                x0 = 0
            else:
                x0 = int(round(x_size * (0.25 + fudge)))
            if (side + 1) % 6 in hexsides:
                x1 = x_size
            else:
                x1 = int(round(x_size * (0.75 - fudge)))
            height = y_size / 2
            box = (x0, 0, x1, height)
            clipboard_im = input_im.crop(box)
            output_im.paste(clipboard_im, box)
    # Rotate back to original orientation
    if last != 0:
        rotation = -60 * last
        output_im = output_im.rotate(rotation)
    output_im.save(output_path)

def main():
    assert len(sys.argv) >= 4
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    hexsides = set()
    for arg in sys.argv[3:]:
        hexside = int(arg)
        assert 0 <= hexside <= 5
        hexsides.add(hexside)
    slice_border_image(input_path, output_path, hexsides)

if __name__ == "__main__":
    main()
