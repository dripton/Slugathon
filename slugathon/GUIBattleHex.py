try:
    import pygtk
    pygtk.require("2.0")
except (ImportError, AttributeError):
    pass
import gtk
import os
import math
import guiutils
import colors

SQRT3 = math.sqrt(3.0)
RAD_TO_DEG = 180. / math.pi

# Where to place the label, by hexside.  Derived experimentally.
x_font_position = [0.5, 0.75, 0.75, 0.5, 0.25, 0.25]
y_font_position = [0.1, 0.125, 0.875, 0.95, 0.875, 0.125]

rp = guiutils.roundpoint


class GUIBattleHex(object):
    def __init__(self, battlehex, guimap):
        self.battlehex = battlehex
        self.guimap = guimap
        scale = self.guimap.scale
        # Leftmost point
        self.cx = battlehex.x * 3 * scale
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
        self.init_overlay()

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


    def draw_hexagon(self, gc, style):
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


    def init_overlay(self):
        """Setup the overlay with terrain name and image."""
        overlay_filename = self.battlehex.overlay_filename
        if overlay_filename is None:
            return
        scale = self.guimap.scale

        myboxsize = [0.85 * mag for mag in self.bboxsize]
        self.dest_x = int(round(self.center[0] - myboxsize[0] / 2.))
        self.dest_y = int(round(self.center[1] - myboxsize[1] / 2.))

        image_filename = os.path.join("../images/battlehex", 
          overlay_filename)
        pixbuf = gtk.gdk.pixbuf_new_from_file(image_filename)
        self.pixbuf = pixbuf.scale_simple(int(round(myboxsize[0])),
            int(round(myboxsize[1])), gtk.gdk.INTERP_BILINEAR)


    def draw_overlay(self, gc, style):
        if self.battlehex.overlay_filename is None:
            return
        drawable = self.guimap.area.window
        drawable.draw_pixbuf(gc, self.pixbuf, 0, 0, self.dest_x, self.dest_y,
          -1, -1, gtk.gdk.RGB_DITHER_NORMAL, 0, 0)


    def draw_label(self, gc, style):
        """Display the hex label."""
        label = str(self.battlehex.label)
        layout = self.guimap.area.create_pango_layout(label)
        text_width, text_height = layout.get_pixel_size()
        half_text_width = 0.5 * text_width
        half_text_height = 0.5 * text_height
        side = self.battlehex.label_side

        x = int(round((self.cx + self.bboxsize[0] * x_font_position[side] -
                half_text_width)))
        y = int(round((self.cy + self.bboxsize[1] * y_font_position[side] -
                half_text_height)))

        colormap = self.guimap.area.get_colormap()
        fg = colormap.alloc_color("black")
        gc.foreground = fg

        self.guimap.area.window.draw_layout(gc, x, y, layout)


    def update_gui(self, gc, style):
        self.draw_hexagon(gc, style)
        self.draw_overlay(gc, style)
        self.draw_label(gc, style)

    def toggle_selection(self):
        self.selected = not self.selected

    def __repr__(self):
        return "GUIBattleHex %s" % self.battlehex.label
