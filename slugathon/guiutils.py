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
