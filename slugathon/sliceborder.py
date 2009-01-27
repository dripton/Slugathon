#!/usr/bin/env python

"""Copy only the specified hexsides from a battlehex border image into
a new image, leaving the rest transparent."""

__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import sys

import cairo


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

    vertexes = []
    vertexes.append((0.25 * x_size, 0))
    vertexes.append((0.75 * x_size, 0))
    vertexes.append((x_size, 0.5 * y_size))
    vertexes.append((0.75 * x_size, y_size))
    vertexes.append((0.25 * x_size, y_size))
    vertexes.append((0, 0.5 * y_size))
    center = (0.5 * x_size, 0.5 * y_size)

    color = (0, 0, 0)
    output_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, x_size, y_size)
    output_ctx = cairo.Context(output_surface)

    for hexside in hexsides:
        output_ctx.move_to(*center)
        output_ctx.line_to(*vertexes[hexside])
        output_ctx.line_to(*vertexes[(hexside + 1) % 6])
        output_ctx.close_path()
    output_ctx.clip()

    output_ctx.move_to(0, 0)
    output_ctx.set_source_surface(input_surface)
    output_ctx.paint()
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
