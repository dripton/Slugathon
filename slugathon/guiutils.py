import Image
import ImageTk


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

