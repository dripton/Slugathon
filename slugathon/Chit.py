try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import Image
import guiutils
import colors

CHIT_SCALE_FACTOR = 3

class Chit(object):
    IMAGE_DIR = "creature"

    """Clickable GUI creature chit"""
    def __init__(self, creature, playercolor, scale=15):
        self.creature = creature
        if creature is None:
            self.name = "QuestionMarkMask"
        else:
            self.name = creature.name
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        bases = [self.name]
        if creature:
            color_name = creature.color_name
            if creature.flies and creature.rangestrikes:
                bases.append("FlyingRangestrikeBase")
            elif creature.flies:
                bases.append("FlyingBase")
            elif creature.rangestrikes:
                bases.append("RangestrikeBase")
        else:
            color_name = "black"
        if color_name == "by_player":
            color_name = "titan_%s" % playercolor.lower()
        rgb = colors.rgb_colors[color_name]

        paths = ["../images/%s/%s.png" % (self.IMAGE_DIR, base)
          for base in bases]
        image = Image.open(paths[0]).convert("RGBA")
        print paths[0], "mode", image.mode, "size", image.size
        for path in paths[1:]:
            mask = Image.open(path).convert("RGBA")
            print path, "mode", mask.mode, "size", mask.size
            image.paste(rgb, None, mask) 
        raw_pixbuf = guiutils.pil_image_to_gdk_pixbuf(image)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
        self.location = None    # (x, y) of top left corner

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def show(self):
        self.image.show()
