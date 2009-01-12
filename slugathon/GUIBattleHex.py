__copyright__ = "Copyright (c) 2005-2009 David Ripton"
__license__ = "GNU GPL v2"


import os
import math
import sys

import gtk
import cairo

import guiutils
import colors
import sliceborder
import Chit

SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180. / math.pi

# Where to place the label, by hexside.  Derived experimentally.
x_font_position = [0.5, 0.7, 0.7, 0.5, 0.35, 0.35]
y_font_position = [0.2, 0.2, 0.8, 0.8, 0.8, 0.2]

rp = guiutils.roundpoint

IMAGE_DIR = "../images/battlehex"


class GUIBattleHex(object):
    def __init__(self, battlehex, guimap):
        self.battlehex = battlehex
        self.guimap = guimap
        scale = self.guimap.scale
        # Leftmost point
        self.cx = (battlehex.x + 1) * 3 * scale
        # Uppermost point
        self.cy = battlehex.y * 2 * SQRT3 * scale
        if battlehex.down:
            self.cy += SQRT3 * scale
        self.fillcolor = self.find_fillcolor()
        self.selected = False

        self.init_vertexes()
        self.center = rp(guiutils.midpoint(self.vertexes[0], self.vertexes[3]))
        self.bboxsize = rp((self.vertexes[2][0] - self.vertexes[5][0],
          self.vertexes[3][1] - self.vertexes[0][1]))
        self.hex_pixbuf = None
        self.hex_pixbuf_x = None
        self.hex_pixbuf_y = None
        self.border_pixbufs = []
        self.border_pixbuf_x = None
        self.border_pixbuf_y = None
        self.init_hex_overlay()
        self.init_border_overlays()

    def find_fillcolor(self):
        terrain = self.battlehex.terrain
        color = colors.battle_terrain_colors.get((terrain,
          self.battlehex.elevation), None)
        if not color:
            color = colors.battle_terrain_colors.get(terrain)
        return guiutils.rgb_to_float(colors.rgb_colors[color])

    def init_vertexes(self):
        """Setup the hex vertexes.

        Each vertex is the midpoint between the vertexes of the two
        bordering hexes.
        """
        self.vertexes = []
        for unused in xrange(6):
            self.vertexes.append(None)
        cx = self.cx
        cy = self.cy
        scale = self.guimap.scale
        self.vertexes[0] = rp((cx + scale, cy))
        self.vertexes[1] = rp((cx + 3 * scale, cy))
        self.vertexes[2] = rp((cx + 4 * scale, cy + SQRT3 * scale))
        self.vertexes[3] = rp((cx + 3 * scale, cy + 2 * SQRT3 * scale))
        self.vertexes[4] = rp((cx + scale, cy + 2 * SQRT3 * scale))
        self.vertexes[5] = rp((cx, cy + SQRT3 * scale))

        self.points = []
        iv = guiutils.scale_polygon(self.vertexes, 0.9)
        for point in iv:
            self.points.append(rp(point))

    @property
    def bounding_rect(self):
        """Return the bounding rectangle (x, y, width, height) of this hex."""
        scale = self.guimap.scale
        min_x = sys.maxint
        max_x = -sys.maxint
        min_y = sys.maxint
        max_y = -sys.maxint
        for x, y in self.vertexes:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        return min_x, min_y, max_x - min_x, max_y - min_y

    def draw_hexagon(self, cr):
        """Create the polygon, filled with the terrain color."""

        if self.selected:
            # outline
            cr.set_source_rgb(1, 0, 0)
            guiutils.draw_polygon(cr, self.points)
            cr.stroke()
            # outer portion
            cr.set_source_rgb(1, 1, 1)
            guiutils.draw_polygon(cr, self.points)
            cr.fill()
            # inner hex
            cr.set_source_rgb(*self.fillcolor)
            guiutils.draw_polygon(cr, self.points)
            cr.fill()
        else:
            # hex
            cr.set_source_rgb(*self.fillcolor)
            guiutils.draw_polygon(cr, self.points)
            cr.fill()
            # outline
            cr.set_source_rgb(1, 1, 1)
            guiutils.draw_polygon(cr, self.points)
            cr.stroke()


    def init_hex_overlay(self):
        """Setup the overlay with terrain name and image."""
        overlay_filename = "%s.png" % self.battlehex.terrain
        image_path = os.path.join(IMAGE_DIR, overlay_filename)
        if not os.path.exists(image_path):
            return
        myboxsize = [0.85 * mag for mag in self.bboxsize]
        self.hex_pixbuf_x = int(round(self.center[0] - myboxsize[0] / 2.))
        self.hex_pixbuf_y = int(round(self.center[1] - myboxsize[1] / 2.))
        pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
        self.hex_pixbuf = pixbuf.scale_simple(int(round(myboxsize[0])),
            int(round(myboxsize[1])), gtk.gdk.INTERP_BILINEAR)

    def init_border_overlays(self):
        """Setup the overlays for each border."""
        myboxsize = [0.97 * mag for mag in self.bboxsize]
        self.border_pixbuf_x = int(round(self.center[0] - myboxsize[0] / 2.))
        self.border_pixbuf_y = int(round(self.center[1] - myboxsize[1] / 2.))
        for hexside, border in enumerate(self.battlehex.borders):
            border_pixbuf = None
            overlay_filename = "%s.png" % border
            image_path = os.path.join(IMAGE_DIR, overlay_filename)
            if os.path.exists(image_path):
                hexsides = self.battlehex.hexsides_with_border(border)
                hexsides_str = "".join(map(str, sorted(hexsides)))
                border_filename = "%s-%s.png" % (border, hexsides_str)
                border_path = os.path.join(IMAGE_DIR, border_filename)
                if not os.path.exists(border_path):
                    sliceborder.slice_border_image(image_path, border_path,
                      hexsides)
                pixbuf = gtk.gdk.pixbuf_new_from_file(border_path)
                border_pixbuf = pixbuf.scale_simple(
                  int(round(myboxsize[0])), int(round(myboxsize[1])),
                  gtk.gdk.INTERP_BILINEAR)
            self.border_pixbufs.append(border_pixbuf)

    def draw_hex_overlay(self, cr):
        """Draw the main terrain overlay for the hex."""
        if self.hex_pixbuf is None:
            return
        cr.set_source_pixbuf(self.hex_pixbuf, self.hex_pixbuf_x,
          self.hex_pixbuf_y)
        cr.paint()

    def draw_border_overlays(self, cr):
        """Draw the overlays for all borders that have them."""
        for hexside, border in enumerate(self.battlehex.borders):
            if border:
                cr.set_source_pixbuf(self.border_pixbufs[hexside],
                  self.border_pixbuf_x, self.border_pixbuf_y)
                cr.paint()

    def draw_label(self, cr, label, side):
        """Display the hex label."""
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL,
          cairo.FONT_WEIGHT_BOLD)
        # TODO Vary font size with scale
        cr.set_font_size(14)

        x_bearing, y_bearing, text_width, text_height = cr.text_extents(
          label)[:4]
        half_text_width = 0.5 * text_width
        half_text_height = 0.5 * text_height

        x = int(round((self.cx + self.bboxsize[0] * x_font_position[side] -
                half_text_width - x_bearing)))
        y = int(round((self.cy + self.bboxsize[1] * y_font_position[side] -
                half_text_height - y_bearing)))

        cr.set_source_rgb(0, 0, 0)
        cr.move_to(x, y)
        cr.show_text(label)


    # TODO save computations
    def highlight_entrance(self, cr):
        """Highlight this entrance hex, if selected"""
        chit_scale = self.guimap.scale * Chit.CHIT_SCALE_FACTOR
        x = self.center[0] - chit_scale / 4
        y = self.center[1] - chit_scale * 7 / 4
        width = chit_scale / 2
        height = 7 * chit_scale / 2
        x1 = x + width
        y1 = y + height
        points = [(x, y), (x1, y), (x1, y1), (x, y1)]
        colormap = self.guimap.area.get_colormap()
        if self.selected:
            # outline
            cr.set_source_rgb(1, 0, 0)
            guiutils.draw_polygon(cr, points)
            cr.stroke()
            # outer portion
            cr.set_source_rgb(1, 1, 1)
            guiutils.draw_polygon(cr, points)
            cr.fill()
            # inner hex
            cr.set_source_rgb(*self.fillcolor)
            guiutils.draw_polygon(cr, points)
            cr.fill()

    def cleanup_entrance(self, cr):
        """Cleanup after any chits that may have moved away from an
        entrance."""
        chit_scale = self.guimap.scale * Chit.CHIT_SCALE_FACTOR
        x = self.center[0] - chit_scale / 2
        y = self.center[1] - chit_scale * 7 / 2
        width = chit_scale
        height = 7 * chit_scale
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, width, height)
        cr.fill()

    def update_gui(self, cr):
        if self.battlehex.visible:
            self.draw_hexagon(cr)
            self.draw_hex_overlay(cr)
            self.draw_border_overlays(cr)
            self.draw_label(cr, self.battlehex.label,
              self.battlehex.label_side)
            self.draw_label(cr, self.battlehex.terrain,
              self.battlehex.terrain_side)
        else:
            self.cleanup_entrance(cr)
            self.highlight_entrance(cr)

    def __repr__(self):
        return "GUIBattleHex %s" % self.battlehex.label
