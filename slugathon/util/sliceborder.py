#!/usr/bin/env python3


import argparse
from typing import List, Set, Tuple

import cairo

__copyright__ = "Copyright (c) 2005-2021 David Ripton"
__license__ = "GNU GPL v2"


"""Copy only the specified hexsides from a battlehex border image into
a new image, leaving the rest transparent."""


def slice_border_image(
    input_path: str, output_path: str, hexsides: Set[int]
) -> None:
    """Copy only the specified hexsides from a battlehex border image into
    a new image, leaving the rest transparent.

    input_path is the path to the input border image.
    output_path is the path to the output border image.
    hexsides is a non-empty set of border hexsides to copy, each in the
    range 0 (north) through 5 (northwest), counting clockwise.
    """
    input_surface = cairo.ImageSurface.create_from_png(input_path)
    x_size = int(input_surface.get_width())
    y_size = int(input_surface.get_height())

    vertexes = []  # type: List[Tuple[float, float]]
    vertexes.append((0.25 * x_size, 0))
    vertexes.append((0.75 * x_size, 0))
    vertexes.append((x_size, 0.5 * y_size))
    vertexes.append((0.75 * x_size, y_size))
    vertexes.append((0.25 * x_size, y_size))
    vertexes.append((0, 0.5 * y_size))
    center = (0.5 * x_size, 0.5 * y_size)

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-path")
    parser.add_argument("-o", "--output-path")
    parser.add_argument("hexsides", type=int, nargs="+")
    args = parser.parse_args()
    if not args.input_path or not args.output_path or not args.hexsides:
        parser.error("Must provide input_path, output_path and hexsides")
    for hexside in args.hexsides:
        if hexside < 0 or hexside > 5:
            parser.error("Hexsides must be in range 0-5 inclusive.")
    slice_border_image(args.input_path, args.output_path, args.hexsides)


if __name__ == "__main__":
    main()
