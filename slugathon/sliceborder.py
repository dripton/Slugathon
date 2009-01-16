#!/usr/bin/env python

"""Copy only the specified hexsides from a battlehex border image into
a new image, leaving the rest transparent."""

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import sys
import math

import cairo

# one-sixth of a circle
PI_DIV_3 = math.pi / 3

def slice_border_image(input_path, output_path, hexsides):
    """Copy only the specified hexsides from a battlehex border image into
    a new image, leaving the rest transparent.

    input_path is the path to the input border image.
    output_path is the path to the output border image.
    hexsides is a non-empty set of border hexsides to copy, each in the
    range 0 (north) through 5 (northwest), counting clockwise.
    """
    input_surface = cairo.ImageSurface.create_from_png(input_path)
    x_size = input_surface.get_width()
    y_size = input_surface.get_height()
    color = (0, 0, 0)
    output_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, x_size, y_size)
    input_cr = cairo.Context(input_surface)
    output_cr = cairo.Context(output_surface)

    last = 0
    for side in xrange(6):
        if side in hexsides:
            if side != 0:
                rotation = PI_DIV_3 * (side - last)
                input_cr.rotate(rotation)
                output_cr.rotate(rotation)
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
            box = (x0, 0, x1 - x0, height)
            input_cr.save()
            input_cr.rectangle(*box)
            input_cr.clip()
            output_cr.move_to(x0, 0)
            output_cr.set_source_surface(input_surface)
            output_cr.fill()
            input_cr.restore()
    # Rotate back to original orientation
    if last != 0:
        rotation = -PI_DIV_3 * last
        output_cr.rotate(rotation)
    output_surface.write_to_png(output_path)

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
