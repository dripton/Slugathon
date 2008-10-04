import os
import math

import gtk

import guiutils
import colors
import sliceborder

SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180. / math.pi

# Where to place the label, by hexside.  Derived experimentally.
x_font_position = [0.5, 0.7, 0.7, 0.5, 0.3, 0.3]
y_font_position = [0.2, 0.2, 0.8, 0.85, 0.8, 0.2]

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
        return guiutils.rgb_to_gtk(colors.rgb_colors[color])

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

        self.inner_vertexes = []
        iv = guiutils.scale_polygon(self.vertexes, 0.9)
        for point in iv:
            self.inner_vertexes.append(rp(point))

        self.points = self.inner_vertexes[:]


    def draw_hexagon(self, gc):
        """Create the polygon, filled with the terrain color."""

        # TODO Fix random black/white edge color on border between selected
        # and unselected hexes.

        colormap = self.guimap.area.get_colormap()

        if self.selected:
            # outer portion
            fg = colormap.alloc_color("white")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True, self.points)

            # inner hex
            fg = colormap.alloc_color(*self.fillcolor)
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True, self.inner_vertexes)

            # outline
            fg = colormap.alloc_color("black")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, False, self.points)

        else:
            # hex
            fg = colormap.alloc_color(*self.fillcolor)
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, True, self.points)

            # outline
            fg = colormap.alloc_color("white")
            gc.foreground = fg
            self.guimap.area.window.draw_polygon(gc, False, self.points)


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
                border_filename = "%s-%d.png" % (border, hexside)
                border_path = os.path.join(IMAGE_DIR, border_filename)
                sliceborder.slice_border_image(image_path, border_path,
                  self.battlehex.hexsides_with_border(border))
                pixbuf = gtk.gdk.pixbuf_new_from_file(border_path)
                border_pixbuf = pixbuf.scale_simple(
                  int(round(myboxsize[0])), int(round(myboxsize[1])),
                  gtk.gdk.INTERP_BILINEAR)
            self.border_pixbufs.append(border_pixbuf)

    def draw_hex_overlay(self, gc):
        """Draw the main terrain overlay for the hex."""
        if self.hex_pixbuf is None:
            return
        drawable = self.guimap.area.window
        drawable.draw_pixbuf(gc, self.hex_pixbuf, 0, 0, self.hex_pixbuf_x,
          self.hex_pixbuf_y, -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

    def draw_border_overlays(self, gc):
        """Draw the overlays for all borders that have them."""
        for hexside, border in enumerate(self.battlehex.borders):
            if border:
                drawable = self.guimap.area.window
                drawable.draw_pixbuf(gc, self.border_pixbufs[hexside], 0, 0, 
                  self.border_pixbuf_x, self.border_pixbuf_y, -1, -1, 
                  gtk.gdk.RGB_DITHER_NORMAL, 0, 0)

    def draw_label(self, gc, label, side):
        """Display the hex label."""
        layout = self.guimap.area.create_pango_layout(label)
        text_width, text_height = layout.get_pixel_size()
        half_text_width = 0.5 * text_width
        half_text_height = 0.5 * text_height

        x = int(round((self.cx + self.bboxsize[0] * x_font_position[side] -
                half_text_width)))
        y = int(round((self.cy + self.bboxsize[1] * y_font_position[side] -
                half_text_height)))

        colormap = self.guimap.area.get_colormap()
        fg = colormap.alloc_color("black")
        gc.foreground = fg

        self.guimap.area.window.draw_layout(gc, x, y, layout)


    def update_gui(self, gc):
        self.draw_hexagon(gc)
        self.draw_hex_overlay(gc)
        self.draw_border_overlays(gc)
        self.draw_label(gc, self.battlehex.label, self.battlehex.label_side)
        self.draw_label(gc, self.battlehex.terrain,
          self.battlehex.terrain_side)

    def toggle_selection(self):
        self.selected = not self.selected

    def __repr__(self):
        return "GUIBattleHex %s" % self.battlehex.label
