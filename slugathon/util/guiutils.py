__copyright__ = "Copyright (c) 2003-2012 David Ripton"
__license__ = "GNU GPL v2"


import sys
import math

from twisted.internet import reactor


def flatten_point_list(points):
    """Flatten a list of (x, y) tuples into a single tuple"""
    li = []
    for tup in points:
        for item in tup:
            li.append(item)
    return tuple(li)


def rgb_to_gtk(rgb):
    """Convert a tuple of 8-bit decimal RGB color values to 16-bit."""
    li = [256 * value for value in rgb]
    return tuple(li)


def rgb_to_float(rgb):
    """Convert a tuple of 8-bit decimal RGB color values to 0.0 - 1.0."""
    li = [value / 256.0 for value in rgb]
    return tuple(li)


def get_semicircle_points(x0, y0, x1, y1, numpoints=8):
    """Return a list of integer 2-tuple points along the semicircle that
    has (x0, y0) and (x1, y1) on opposite sides, going clockwise.
    """
    if numpoints <= 0:
        return []
    xcenter = (x0 + x1) / 2.
    ycenter = (y0 + y1) / 2.
    radius = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) / 2.

    # Reverse signs of y because vertical screen coords increase down.
    theta0 = math.atan2((ycenter - y0), (x0 - xcenter))
    theta1 = math.atan2((ycenter - y1), (x1 - xcenter))
    del_theta = (theta1 - theta0) / (numpoints - 1)
    if del_theta > 0:
        del_theta = -del_theta

    xlist = []
    ylist = []
    theta = theta0
    for unused in xrange(numpoints):
        xlist.append(int(round(xcenter + math.cos(theta) * radius)))
        ylist.append(int(round(ycenter - math.sin(theta) * radius)))
        theta += del_theta
    return zip(xlist, ylist)


def scale_polygon(vertexes, ratio):
    """Return a rescaled version of the polygon, with the same center."""
    totalx = 0
    totaly = 0
    for (px, py) in vertexes:
        totalx += px
        totaly += py
    center = (totalx / len(vertexes), totaly / len(vertexes))
    nv = []
    for (px, py) in vertexes:
        deltax = (px - center[0]) * ratio
        deltay = (py - center[1]) * ratio
        nv.append((center[0] + deltax, center[1] + deltay))
    return nv


def point_in_square(point, topleft, length):
    return (point[0] >= topleft[0] and point[1] >= topleft[1] and
      point[0] < topleft[0] + length and point[1] < topleft[1] + length)


def point_in_polygon(point, vertexes):
    """Return True iff the point (a 2-tuple) is in the polygon specified
    by vertexes (a sequence of 2-tuples).

    Based on C code from http://www.faqs.org/faqs/graphics/algorithms-faq/
    """
    npol = len(vertexes)
    x, y = point
    c = False
    for i, (xi, yi) in enumerate(vertexes):
        j = (i + 1) % npol
        xj, yj = vertexes[j]
        if ((yi <= y < yj or yj <= y < yi) and
          (x < 1.0 * (xj - xi) * (y - yi) / (yj - yi) + xi)):
            c = not c
    return c


def midpoint(point1, point2):
    """Return a point midway between two points."""
    xx = (point1[0] + point2[0]) / 2.
    yy = (point1[1] + point2[1]) / 2.
    return (xx, yy)


def roundpoint(point):
    """Return a point with both coordinates rounded to integers."""
    return (int(round(point[0])), int(round(point[1])))


def exit(*unused):
    """Quit the program with return status 0.

    Used because sys.exit takes an argument, but it's not always
    convenient to pass one through a callback.
    """
    if reactor.running:
        reactor.stop()
    else:
        sys.exit(0)


def draw_polygon(ctx, points):
    """Draw a polygon using Cairo"""
    ctx.move_to(*points[0])
    for point in points[1:]:
        ctx.line_to(*point)
    ctx.close_path()


def rectangles_intersect(rect1, rect2):
    """Return True iff the two rectangles intersect"""
    x1, y1, width1, height1 = rect1
    x2, y2, width2, height2 = rect2
    if x1 + width1 < x2 or x2 + width2 < x1:
        return False
    if y1 + height1 < y2 or y2 + height2 < y1:
        return False
    return True


def combine_rectangles(rect1, rect2):
    """Return the smallest rectangle containing both passed rectangles."""
    x1, y1, width1, height1 = rect1
    x2, y2, width2, height2 = rect2
    x = min(x1, x2)
    y = min(y1, y2)
    max_x = max(x1 + width1, x2 + width2)
    width = max_x - x
    max_y = max(y1 + height1, y2 + height2)
    height = max_y - y
    return x, y, width, height
