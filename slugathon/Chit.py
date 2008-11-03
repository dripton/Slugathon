import gtk
import Image
import ImageFont
import ImageDraw

import guiutils
import colors

CHIT_SCALE_FACTOR = 3

red = colors.rgb_colors["red"]
white = colors.rgb_colors["white"]

class Chit(object):
    """Clickable GUI creature chit"""

    IMAGE_DIR = "creature"

    def __init__(self, creature, playercolor, scale=15, dead=False,
      rotate=None):
        self.creature = creature
        if creature is None:
            self.name = "QuestionMarkMask"
        else:
            self.name = creature.name
        self.dead = dead
        self.rotate = rotate
        self.location = None    # (x, y) of top left corner
        self.chit_scale = CHIT_SCALE_FACTOR * scale

        self.bases = [self.name]
        if creature:
            color_name = creature.color_name
            if creature.flies and creature.rangestrikes:
                self.bases.append("FlyingRangestrikeBase")
            elif creature.flies:
                self.bases.append("FlyingBase")
            elif creature.rangestrikes:
                self.bases.append("RangestrikeBase")
        else:
            color_name = "black"
        if color_name == "by_player":
            color_name = "titan_%s" % playercolor.lower()
        self.rgb = colors.rgb_colors[color_name]

        self.paths = ["../images/%s/%s.png" % (self.IMAGE_DIR, base)
          for base in self.bases]

        self.event_box = gtk.EventBox()
        self.event_box.chit = self
        self.image = gtk.Image()
        self.event_box.add(self.image)
        self._build_image()

    def _build_image(self):
        im = Image.open(self.paths[0]).convert("RGBA")
        for path in self.paths[1:]:
            mask = Image.open(path).convert("RGBA")
            im.paste(self.rgb, None, mask)
        self._render_text(im, self.rgb)
        if self.dead:
            self._render_x(im)
        elif self.creature and self.creature.hits > 0:
            self._render_hits(im)
        raw_pixbuf = guiutils.pil_image_to_gdk_pixbuf(im)
        self.pixbuf = raw_pixbuf.scale_simple(self.chit_scale,
          self.chit_scale, gtk.gdk.INTERP_BILINEAR)
        if self.rotate:
            self.pixbuf = self.pixbuf.rotate_simple(self.rotate)
        self.image.set_from_pixbuf(self.pixbuf)

    def point_inside(self, point):
        assert self.location
        return guiutils.point_in_square(point, self.location, self.chit_scale)

    def show(self):
        self.event_box.show()
        self.image.show()

    def connect(self, event, method):
        self.event_box.connect(event, method)

    def _render_text(self, im, rgb):
        """Add creature name, power, and toughness to Image im"""
        if not self.creature:
            return
        font_path = "../fonts/VeraSeBd.ttf"
        # TODO Vary font size with scale
        font_size = 9
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(im)
        leng = im.size[0]

        # Name
        if self.name != "Titan":
            label = self.name.upper()
            text_width, text_height = draw.textsize(label, font=font)
            # TODO If text_width is too big, try a smaller font
            x = 0.5 * leng - 0.5 * text_width
            y = 0.125 * leng - 0.5 * text_height
            draw.text((x, y), label, fill=rgb, font=font)

        # Power
        label = str(self.creature.power)
        text_width, text_height = draw.textsize(label, font=font)
        x = 0.1 * leng - 0.5 * text_width
        y = 0.9 * leng - 0.5 * text_height
        draw.text((x, y), label, fill=rgb, font=font)

        # Skill
        label = str(self.creature.skill)
        text_width, text_height = draw.textsize(label, font=font)
        x = 0.9 * leng - 0.5 * text_width
        y = 0.9 * leng - 0.5 * text_height
        draw.text((x, y), label, fill=rgb, font=font)

    def _render_x(self, im):
        """Add a big red X through Image im"""
        draw = ImageDraw.Draw(im)
        draw.line((0, 0) + im.size, fill=red, width=2)
        draw.line((0, im.size[1], im.size[0], 0), fill=red, width=2)

    def _render_hits(self, im):
        """Add the number of hits to Image im"""
        if not self.creature or not self.creature.hits:
            return
        font_path = "../fonts/VeraSeBd.ttf"
        # TODO Vary font size with scale
        font_size = 30
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(im)
        leng = im.size[0]

        label = str(self.creature.hits)
        text_width, text_height = draw.textsize(label, font=font)
        x = 0.5 * leng - 0.5 * text_width
        y = 0.5 * leng - 0.5 * text_height
        draw.rectangle(((x + 0.1 * text_width, y + 0.2 * text_height),
          (x + 0.9 * text_width, y + 0.8 * text_height)), fill=white)
        draw.text((x, y), label, fill=red, font=font)
