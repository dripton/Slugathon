#!/usr/bin/env python

"""Make parts of a hexside border image transparent, so that only the
specified borders are visible."""

import sys

import Image


def slice_border_image(input_path, output_path, hexsides):
    """Make parts of a hexside border image transparent, so that only the
    specified borders are visible.
    
    input_path is the path to the input border image.
    output_path is the path to the output border image.
    hexsides is a non-empty set of border hexsides to keep, each in the 
    range 0 (north) through 5 (northwest), counting clockwise.
    """
    im = Image.open(input_path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
        assert im.mode == "RGBA"
    x_size, y_size = im.size
    last = 0
    for side in xrange(6):
        if side not in hexsides:
            if side != 0:
                rotation = 60 * (side - last)
                im = im.rotate(rotation)
                last = side
            color = (0, 0, 0, 0)
            # Determined experimentally.
            height = y_size / 8
            box = (0, 0, x_size, height)
            im.paste(color, box)
    # Rotate back to original orientation
    if last != 0:
        rotation = -60 * last
        im = im.rotate(rotation)
    im.save(output_path)

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
