# TODO show titan power

try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import Image
import ImageFont
import ImageDraw

import colors
import guiutils

CHIT_SCALE_FACTOR = 3

black = colors.rgb_colors["black"]
white = colors.rgb_colors["white"]


class Marker(object):
    """Clickable GUI legion marker"""
    def __init__(self, legion, show_height, scale=15):
        self.legion = legion
        self.name = legion.markername
        self.chit_scale = CHIT_SCALE_FACTOR * scale
        self.show_height = show_height
        self.image_path = "../images/legion/%s.png" % self.name
        self.location = None    # (x, y) of top left corner
        self.build_image()

    def build_image(self):
        self.height = len(self.legion)
        im = Image.open(self.image_path).convert("RGBA")
        self._render_text(im)
        raw_pixbuf = guiutils.pil_image_to_gdk_pixbuf(im)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        self.event_box = gtk.EventBox()
        self.event_box.marker = self
        self.image = gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
        self.event_box.add(self.image)

    def __repr__(self):
        return "Marker %s in %s" % (self.name, self.legion.hexlabel)

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def update_height(self):
        if self.show_height and self.height != len(self.legion):
            self.build_image()

    def show(self):
        self.event_box.show()
        self.image.show()

    def connect(self, event, method):
        self.event_box.connect(event, method)

    def _render_text(self, im):
        """Add legion height to Image im"""
        if not self.show_height:
            return
        font_path = "../fonts/VeraSeBd.ttf"
        # TODO Vary font size with scale
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(im)
        leng = im.size[0]

        label = str(self.height)
        text_width, text_height = draw.textsize(label, font=font)
        x = 0.65 * leng - 0.5 * text_width
        y = 0.55 * leng - 0.5 * text_width
        draw.rectangle(((x + 0.1 * text_width, y + 0.1 * text_height), 
          (x + 0.9 * text_width, y + 0.9 * text_height)), fill=white)
        draw.text((x, y), label, fill=black, font=font)
