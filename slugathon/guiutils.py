import math
import Image
import StringIO


IMAGE_DIR = '../images/'

def flatten_point_list(points):
    """Flatten a list of (x, y) tuples into a single tuple"""
    li = []
    for tup in points:
        for item in tup:
            li.append(item)
    return tuple(li)

def RgbToTk(rgb):
    """Convert a tuple of decimal RGB color values to a Tk color string"""
    return "#%02X%02X%02X" % rgb

def RgbToGtk(rgb):
    """Convert a tuple of 8-bit decimal RGB color values 16-bit."""
    li = [256 * value for value in rgb]
    return tuple(li)

def ImageToGdkPixbuf(image):
    file = StringIO.StringIO()
    image.save(file, 'ppm')
    contents = file.getvalue()
    file.close()
    loader = gtk.gdk.PixbufLoader('pnm')
    loader.write(contents, len(contents))
    pixbuf = loader.get_pixbuf()
    loader.close()
    return pixbuf




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
    for i in xrange(numpoints):
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

def point_in_polygon(point, vertexes):
    """Return True iff the point (a 2-tuple) is in the polygon specified
       by vertexes (a sequence of 2-tuples).
    """
    # Test against the polygon's bounding box.
    xs = [x for (x, y) in vertexes]
    ys = [y for (x, y) in vertexes]
    minX = min(xs)
    minY = min(ys)
    maxX = max(xs)
    maxY = max(ys)
    (px, py) = point
    if px < minX or px >= maxX or py < minY or py >= maxY:
        return False

    # Draw a ray due east from point, and see how many lines it crosses.
    # Treat intervals as closed on the low end, open on the high end.
    crossings = 0
    numpoints = len(vertexes)
    for i in range(numpoints):
        j = (i + 1) % numpoints
        (xi, yi) = vertexes[i]
        (xj, yj) = vertexes[j]
        if (yi < py and yj < py) or (yi >= py and yj >= py):
            # No intersection possible.
            continue
        if xi >= px and xj >= px:
            crossings += 1
    return crossings & 1
